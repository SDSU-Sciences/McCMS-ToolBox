#!/usr/bin/env python3
"""
wp_to_pcfmult.py

Batch convert WordPress faculty profile HTML files to PCF files using
template-pcfGen.txt placeholders (e.g. ||| E-mail |||, ||| Education |||).

Usage:
  python wp_to_pcfmult.py profiles template-pcfGen.txt

Output:
  output/<first>-<last>.pcf  (falls back to <html_stem>.pcf)

Notes:
- Missing HTML fields -> blank in output.
- Replaces placeholders inside ||| ... ||| using PLACEHOLDER_TO_KEY mapping.
- Also fills common OUC editor/div regions if present in template.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup

OUTPUT_DIR = Path("output")

# -----------------------
# Template placeholders (MUST match exact text inside your ||| ... |||)
# These were taken from your template-pcfGen.txt style (e.g. "First Name", "Phone Number", etc.)
PLACEHOLDER_TO_KEY = {
    # Identity
    "First Name": "first_name",
    "Last Name": "last_name",
    "Display Name": "display_name",
    "Suffix": "suffix",
    "Pronouns": "pronouns",
    "Title": "title",

    # Org
    "Program Area": "program_area",
    "Organizational Unit": "organizational_unit",
    "Department": "department",
    "Division": "division",
    "Affiliation": "affiliation",

    # Contact
    "E-mail": "email",
    "Phone Number": "phone",
    "Mail Code": "mail_code",
    "Office Hours": "office_hours",

    # Location/address (optional – blank if not detected)
    "Building/Location": "building",
    "Campus": "campus",
    "Street Address Line 1": "street_1",
    "Street Address Line 2": "street_2",
    "City": "city",
    "State": "state",
    "Zip Code": "zip",

    # Content
    "Bio": "bio",
    "Education": "education",
    "Fun Facts": "fun_fact",
    "Research": "research",
    "Publications": "publications",
    "Mentors": "mentors_text",
}

# -----------------------
# Helpers
# -----------------------
def text_or_empty(x) -> str:
    return (x or "").strip()


def safe_slug(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")


def xml_escape(s: str) -> str:
    if s is None:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def join_lines_for_html(s: str) -> str:
    """Multi-line plain text -> <br/> joined, XML-safe."""
    if not s:
        return ""
    lines = [xml_escape(ln.strip()) for ln in s.splitlines() if ln.strip()]
    return "<br/>".join(lines)


def strip_template_placeholders(pcf_text: str) -> str:
    """Remove any leftover ||| ... ||| placeholders."""
    return re.sub(r"\|\|\|.*?\|\|\|", "", pcf_text, flags=re.S)


def normalize_label(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def clean_wp_shortcodes_to_text(s: str) -> str:
    """
    Remove WP shortcodes like:
      [su_accordion] [su_spoiler title="Fun Facts"] ... [/su_spoiler] [/su_accordion]
    leaving ONLY plain text.
    """
    if not s:
        return ""

    # remove specific shortcodes (open/close)
    s = re.sub(r"\[/?su_accordion[^\]]*\]", "", s, flags=re.I)
    s = re.sub(r"\[/?su_spoiler[^\]]*\]", "", s, flags=re.I)

    # remove any shortcode tag: [tag ...] or [/tag]
    s = re.sub(r"\[/?[a-zA-Z_][a-zA-Z0-9_:-]*(?:\s+[^\]]*)?\]", "", s)

    # normalize whitespace
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()


def remove_publications_demo_tokens(pcf_text: str) -> str:
    """
    If your template has demo publications like:
      [A]
      [B]
      [C]
    remove them completely (only when WP has no publications).
    """
    # remove lines that are exactly "[A]" etc
    pcf_text = re.sub(r"(?m)^\s*\[[A-Z]\]\s*$\n?", "", pcf_text)

    # remove inline single-letter bracket tokens
    pcf_text = re.sub(r"\s*\[[A-Z]\]\s*", " ", pcf_text)

    # remove ULs containing only such tokens
    pcf_text = re.sub(
        r"(?is)<ul>\s*(?:<li>\s*\[[A-Z]\]\s*</li>\s*)+</ul>",
        "",
        pcf_text,
    )

    pcf_text = re.sub(r"\n{3,}", "\n\n", pcf_text)
    return pcf_text


# -----------------------
# Extract contact & other fields from WordPress HTML
# -----------------------
def extract_contact_fields(soup: BeautifulSoup) -> Dict[str, str]:
    out = {
        "email": "",
        "phone": "",
        "fax": "",
        "mail_code": "",
        "office_hours": "",
        "location_block": "",
    }

    # mailto / tel links
    a_email = soup.select_one('a[href^="mailto:"]')
    if a_email:
        out["email"] = (a_email.get("href") or "").replace("mailto:", "").strip()

    a_tel = soup.select_one('a[href^="tel:"]')
    if a_tel:
        out["phone"] = (a_tel.get("href") or "").replace("tel:", "").strip()

    # dl/dt/dd structures
    for dl in soup.find_all("dl"):
        for dt in dl.find_all("dt"):
            dd = dt.find_next_sibling("dd")
            if not dd:
                continue
            lbl = normalize_label(dt.get_text(" ", strip=True).rstrip(":"))
            val = dd.get_text("\n", strip=True)

            if lbl in {"email", "e-mail"} and not out["email"]:
                out["email"] = val.strip()
            elif lbl in {"phone", "telephone", "contact", "phone number"} and not out["phone"]:
                out["phone"] = val.strip()
            elif lbl == "fax" and not out["fax"]:
                out["fax"] = val.strip()
            elif lbl in {"mail code", "mailcode"} and not out["mail_code"]:
                out["mail_code"] = val.strip()
            elif lbl in {"office hours", "hours"} and not out["office_hours"]:
                out["office_hours"] = val.strip()
            elif lbl in {"location", "address"} and not out["location_block"]:
                out["location_block"] = val.strip()

    # fallback scan page text
    page_text = soup.get_text("\n", strip=True)

    def find_multiline(label: str) -> str:
        # capture everything after a label line until next known label or end
        labels = [
            "Email", "E-mail", "Phone", "Telephone", "Contact", "Fax", "Mail Code",
            "Office Hours", "Location", "Address"
        ]
        label_union = "|".join(re.escape(x) for x in labels)
        m = re.search(
            rf"(?im)^{re.escape(label)}\s*:?\s*$\n(.*?)(?=^\s*(?:{label_union})\s*:?\s*$|\Z)",
            page_text,
            flags=re.S,
        )
        if not m:
            return ""
        return "\n".join([ln.strip() for ln in m.group(1).splitlines() if ln.strip()])

    def find_singleline(label: str) -> str:
        m = re.search(rf"(?im)^{re.escape(label)}\s*:\s*(.+)$", page_text)
        return m.group(1).strip() if m else ""

    if not out["email"]:
        out["email"] = find_singleline("Email") or find_singleline("E-mail")
    if not out["phone"]:
        out["phone"] = find_singleline("Phone") or find_singleline("Phone Number") or find_singleline("Contact")
    if not out["mail_code"]:
        out["mail_code"] = find_singleline("Mail Code")
    if not out["office_hours"]:
        out["office_hours"] = find_multiline("Office Hours")
    if not out["location_block"]:
        out["location_block"] = find_multiline("Location") or find_multiline("Address")

    return out


def parse_wp_profile(html_text: str) -> Dict:
    soup = BeautifulSoup(html_text, "html.parser")

    # Name in <h1>: "Autumn Askew, M.S."
    h1 = soup.find("h1")
    full_name = text_or_empty(h1.get_text(" ", strip=True) if h1 else "")

    name_part, suffix = full_name, ""
    if "," in full_name:
        name_part, suffix = [p.strip() for p in full_name.split(",", 1)]

    parts = [p for p in name_part.split() if p]
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) >= 2 else (parts[0] if parts else "")

    # Image
    img = soup.select_one(".faculty__image img")
    img_src = (img.get("src") or "").strip() if img else ""
    img_alt = (img.get("alt") or "").strip() if img else ""

    # Header fields from .faculty__heading
    pronouns = title = program_area = department = organizational_unit = division = affiliation = ""
    heading = soup.select_one(".faculty__heading")
    if heading:
        ps = heading.find_all("p")
        # Pronouns line
        if len(ps) >= 1:
            txt = ps[0].get_text(" ", strip=True)
            m = re.search(r"Pronouns:\s*(.+)$", txt)
            pronouns = text_or_empty(m.group(1) if m else "")

        # Title (3rd <p> in your sample)
        if len(ps) >= 3:
            title_lines = [text_or_empty(x) for x in ps[2].stripped_strings]
            # join with " | " like your template expects
            title = " | ".join([t for t in title_lines if t])

        # Program/Department-ish line (4th <p> in your sample)
        if len(ps) >= 4:
            lines = [text_or_empty(x) for x in ps[3].stripped_strings]
            if lines:
                program_area = lines[0]
                # second line becomes department (or specialization-like)
                if len(lines) >= 2:
                    department = lines[1]

        # Region/city line sometimes next
        # (not directly needed for your "org" fields)

    # Office hours
    office_hours = ""
    office = soup.select_one("#hours .faculty__available")
    if office:
        office_hours = text_or_empty(office.get_text("\n", strip=True))

    # Research & Bio (if present)
    research = ""
    r = soup.select_one(".content-expertise p")
    if r:
        research = text_or_empty(r.get_text(" ", strip=True))

    bio = ""
    b = soup.select_one(".content-bio p")
    if b:
        bio = text_or_empty(b.get_text(" ", strip=True))

    # Mentors plain text
    mentors_text = ""
    mentors_p = soup.select_one(".content-messages p")
    if mentors_p:
        mentors_text = text_or_empty(mentors_p.get_text(" ", strip=True))

    # Publications list
    pub_items = [li.get_text(" ", strip=True) for li in soup.select("#publications li.ea-profile-activity")]
    publications = [text_or_empty(p) for p in pub_items if text_or_empty(p)]

    # Education (try common blocks/headings)
    education = ""
    ed_block = soup.select_one(".content-education, .education, #education")
    if ed_block:
        lis = [li.get_text(" ", strip=True) for li in ed_block.select("li")]
        if lis:
            education = " | ".join([text_or_empty(x) for x in lis if text_or_empty(x)])
        else:
            education = text_or_empty(ed_block.get_text(" ", strip=True))
    if not education:
        for htag in ("h2", "h3", "h4"):
            h = soup.find(htag, string=re.compile(r"^\s*Education\s*$", flags=re.I))
            if h:
                vals = []
                node = h.find_next_sibling()
                while node and node.name not in ("h2", "h3", "h4"):
                    vals.append(node.get_text(" ", strip=True))
                    node = node.find_next_sibling()
                education = " | ".join([text_or_empty(v) for v in vals if text_or_empty(v)])
                break

    # Fun facts (clean shortcodes)
    fun_fact = ""
    ff_block = soup.select_one(".content-funfact, .fun-fact, #fun-fact, .funfacts, #funfacts")
    if ff_block:
        fun_fact = text_or_empty(ff_block.get_text(" ", strip=True))
    if not fun_fact:
        for htag in ("h2", "h3", "h4"):
            hff = soup.find(htag, string=re.compile(r"^\s*(Fun Fact|Fun Facts|Interesting Fact)s?\s*$", flags=re.I))
            if hff:
                node = hff.find_next_sibling()
                if node:
                    fun_fact = text_or_empty(node.get_text(" ", strip=True))
                break
    fun_fact = clean_wp_shortcodes_to_text(fun_fact)

    # Contact fields
    contact = extract_contact_fields(soup)
    office_hours_final = office_hours or contact.get("office_hours", "")

    return {
        # identity
        "full_name": full_name,
        "display_name": name_part or full_name,
        "first_name": first,
        "last_name": last,
        "suffix": suffix,
        "pronouns": pronouns,
        "title": title,

        # org
        "program_area": program_area,
        "organizational_unit": organizational_unit,
        "department": department,
        "division": division,
        "affiliation": affiliation,

        # image
        "image_src": img_src,
        "image_alt": img_alt,

        # content
        "bio": bio,
        "research": research,
        "education": education,
        "fun_fact": fun_fact,
        "mentors_text": mentors_text,
        "publications": publications,

        # contact
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
        "mail_code": contact.get("mail_code", ""),
        "office_hours": office_hours_final,

        # optional location/address (leave blank unless you add parsing later)
        "building": "",
        "campus": "",
        "street_1": "",
        "street_2": "",
        "city": "",
        "state": "",
        "zip": "",
    }


# -----------------------
# Template filling helpers
# -----------------------
def replace_metadata_title(pcf: str, new_title: str) -> str:
    pattern = r'(<ouc:properties\s+label="metadata">.*?<title>)(.*?)(</title>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf
    return re.sub(pattern, lambda m: m.group(1) + xml_escape(new_title) + m.group(3), pcf, flags=re.S)


def replace_ouc_div_text(pcf: str, label: str, value: str) -> str:
    pattern = rf'(<ouc:div\s+label="{re.escape(label)}"[^>]*>\s*<ouc:multiedit[^>]*/>)(.*?)(</ouc:div>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf
    return re.sub(pattern, lambda m: m.group(1) + xml_escape(value or "") + m.group(3), pcf, flags=re.S)


def replace_checkbox(pcf: str, label: str, checked: bool) -> str:
    pattern = rf'(<ouc:div\s+label="{re.escape(label)}"[^>]*>\s*<ouc:multiedit[^>]*/>)(.*?)(</ouc:div>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf
    val = "true" if checked else "false"
    return re.sub(pattern, lambda m: m.group(1) + val + m.group(3), pcf, flags=re.S)


def replace_image(pcf: str, src: str, alt: str) -> str:
    pattern = r'(<ouc:div\s+label="image"[^>]*>.*?<img\b)([^>]*)(/?>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf

    def repl(m):
        attrs = m.group(2)
        if re.search(r'\bsrc="[^"]*"', attrs):
            attrs = re.sub(r'\bsrc="[^"]*"', f'src="{xml_escape(src or "")}"', attrs)
        else:
            attrs += f' src="{xml_escape(src or "")}"'

        if re.search(r'\balt="[^"]*"', attrs):
            attrs = re.sub(r'\balt="[^"]*"', f'alt="{xml_escape(alt or "")}"', attrs)
        else:
            attrs += f' alt="{xml_escape(alt or "")}"'

        return m.group(1) + attrs + m.group(3)

    return re.sub(pattern, repl, pcf, flags=re.S)


def replace_ouc_editor_region(pcf: str, label: str, inner_html: str) -> str:
    pattern = rf'(<ouc:div\s+label="{re.escape(label)}"[^>]*>.*?<ouc:editor[^>]*/>)(.*?)(</ouc:div>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf

    def repl(m):
        html = (inner_html or "").strip()
        if html:
            return m.group(1) + "\n" + html + "\n    " + m.group(3)
        return m.group(1) + "\n    " + m.group(3)

    return re.sub(pattern, repl, pcf, flags=re.S)


def build_ul(items: List[str]) -> str:
    if not items:
        return ""
    lis = "\n".join([f"  <li>{xml_escape(it)}</li>" for it in items])
    return "<ul>\n" + lis + "\n</ul>"


def apply_show_flags(pcf: str, data: Dict) -> str:
    # these exist in many OU templates; safe if missing
    pcf = replace_checkbox(pcf, "show-publications", bool(data.get("publications")))
    pcf = replace_checkbox(pcf, "show-research", bool(data.get("research")))
    pcf = replace_checkbox(pcf, "show-education", bool(data.get("education")))
    pcf = replace_checkbox(pcf, "show-fun-facts", bool(data.get("fun_fact")))
    pcf = replace_checkbox(pcf, "show-image", bool(data.get("image_src") or data.get("image_alt")))
    return pcf


def replace_triplebar_placeholders(pcf: str, data: Dict) -> str:
    pattern = r"\|\|\|\s*(.*?)\s*\|\|\|"

    def repl(m: re.Match) -> str:
        token = (m.group(1) or "").strip()
        key = PLACEHOLDER_TO_KEY.get(token)
        if not key:
            return ""

        if key == "publications":
            pubs = data.get("publications", []) or []
            return build_ul(pubs) if pubs else ""

        if key == "office_hours":
            return join_lines_for_html(data.get("office_hours", "") or "")

        # everything else as plain XML-safe text
        return xml_escape(data.get(key, "") or "")

    return re.sub(pattern, repl, pcf)


# -----------------------
# Main conversion per-file
# -----------------------
def html_to_pcf(html_path: Path, template_text: str) -> Tuple[str, str]:
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    data = parse_wp_profile(html_text)

    pcf = template_text

    # metadata title
    title = data.get("display_name") or data.get("full_name") or html_path.stem
    pcf = replace_metadata_title(pcf, title)

    # Fill key OUCampus div fields (these exist in your template)
    pcf = replace_ouc_div_text(pcf, "first-name", data.get("first_name", ""))
    pcf = replace_ouc_div_text(pcf, "last-name", data.get("last_name", ""))
    pcf = replace_ouc_div_text(pcf, "display-name", data.get("display_name", ""))
    pcf = replace_ouc_div_text(pcf, "suffix", data.get("suffix", ""))
    pcf = replace_ouc_div_text(pcf, "pronouns", data.get("pronouns", ""))
    pcf = replace_ouc_div_text(pcf, "title", data.get("title", ""))

    # Org fields (match template labels)
    pcf = replace_ouc_div_text(pcf, "program", data.get("program_area", ""))
    pcf = replace_ouc_div_text(pcf, "unit", data.get("organizational_unit", ""))
    pcf = replace_ouc_div_text(pcf, "department", data.get("department", ""))
    pcf = replace_ouc_div_text(pcf, "division", data.get("division", ""))

    # Contact fields
    pcf = replace_ouc_div_text(pcf, "email", data.get("email", ""))
    pcf = replace_ouc_div_text(pcf, "phone", data.get("phone", ""))
    pcf = replace_ouc_div_text(pcf, "mail-code", data.get("mail_code", ""))

    # Image
    pcf = replace_image(pcf, data.get("image_src", ""), data.get("image_alt", ""))

    # Editor regions (blank if missing)
    bio = data.get("bio", "")
    research = data.get("research", "")
    education = data.get("education", "")
    fun_fact = data.get("fun_fact", "")
    office = data.get("office_hours", "")

    pcf = replace_ouc_editor_region(pcf, "bio", f"<p>{xml_escape(bio)}</p>" if bio else "")
    pcf = replace_ouc_editor_region(pcf, "research", f"<p>{xml_escape(research)}</p>" if research else "")
    pcf = replace_ouc_editor_region(pcf, "education", f"<p>{xml_escape(education)}</p>" if education else "")
    pcf = replace_ouc_editor_region(pcf, "fun-facts", f"<p>{xml_escape(fun_fact)}</p>" if fun_fact else "")
    pcf = replace_ouc_editor_region(pcf, "office-hours", f"<p>{join_lines_for_html(office)}</p>" if office else "")

    # Publications editor region
    pubs = data.get("publications", []) or []
    pubs_html = build_ul(pubs)
    pcf = replace_ouc_editor_region(pcf, "publications", pubs_html if pubs_html else "")

    # Hide empty sections when show-* exists
    pcf = apply_show_flags(pcf, data)

    # Replace ||| ... ||| placeholders
    pcf = replace_triplebar_placeholders(pcf, data)

    # If WP has no publications, remove demo tokens from template
    if not pubs:
        pcf = remove_publications_demo_tokens(pcf)

    # Finally remove any leftover placeholders
    pcf = strip_template_placeholders(pcf)

    # Output filename
    if data.get("first_name") and data.get("last_name"):
        out_name = f"{safe_slug(data['first_name'])}-{safe_slug(data['last_name'])}.pcf"
    else:
        out_name = f"{safe_slug(html_path.stem) or 'profile'}.pcf"

    return out_name, pcf


def collect_html_inputs(arg_paths: List[str]) -> List[Path]:
    files: List[Path] = []
    for raw in arg_paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(p.glob("*.html")))
        elif p.is_file() and p.suffix.lower() == ".html":
            files.append(p)

    seen = set()
    unique: List[Path] = []
    for f in files:
        k = str(f.resolve())
        if k not in seen:
            seen.add(k)
            unique.append(f)
    return unique


def main(argv: List[str]) -> int:
    if len(argv) < 3:
        print(
            "Usage:\n  python wp_to_pcfmult.py <html_or_folder> [more_html_or_folders...] <template-pcfGen.txt>",
            file=sys.stderr,
        )
        return 2

    template_path = Path(argv[-1])
    if not template_path.is_file():
        print(f"Error: template file not found: {template_path}", file=sys.stderr)
        return 2

    inputs = collect_html_inputs(argv[1:-1])
    if not inputs:
        print("Error: no .html files found in the provided inputs.", file=sys.stderr)
        return 2

    template_text = template_path.read_text(encoding="utf-8", errors="ignore")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ok, failed = 0, 0
    for html_path in inputs:
        try:
            out_name, pcf_text = html_to_pcf(html_path, template_text)
            out_path = OUTPUT_DIR / out_name
            out_path.write_text(pcf_text, encoding="utf-8")
            print(f"✅ {html_path.name} -> {out_path}")
            ok += 1
        except Exception as e:
            print(f"❌ Failed on {html_path}: {e}", file=sys.stderr)
            failed += 1

    print(f"\nDone. Generated {ok} PCF file(s) in '{OUTPUT_DIR}/'.")
    if failed:
        print(f"Warnings: {failed} file(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))