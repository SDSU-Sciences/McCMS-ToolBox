#!/usr/bin/env python3
"""
Batch convert WordPress faculty HTML files into PCF files using a TEMPLATE text file.

Your setup:
  - HTML folder: profiles/
  - Template: template-pcfGen.txt (same folder as this script)
  - Output folder: output/ (auto-created)

Run:
  python wp_to_pcfmult.py profiles template-pcfGen.txt

Behavior:
  - Missing HTML fields => blank output
  - If template has show-* checkboxes, they are set false when the field is blank
  - Replaces placeholders like ||| E-mail |||, ||| Phone ||| etc from WP HTML
  - Any leftover placeholder text like ||| ... ||| is removed at the end
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from bs4 import BeautifulSoup

OUTPUT_DIR = Path("output")


# -----------------------
# Placeholder mapping
# -----------------------
# If your template uses slightly different text inside ||| ... |||,
# add it here (left side) and map to the extracted key (right side).
PLACEHOLDER_TO_KEY = {
    "E-mail": "email",
    "Email": "email",
    "Phone": "phone",
    "Contact": "phone",            # sometimes templates label phone as "Contact"
    "Phone Number": "phone",
    "Fax": "fax",
    "Mail Code": "mail_code",
    "Office Hours": "office_hours",
    "Location": "location_block",
}


# -----------------------
# Small helpers
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
    """Escape text for XML (for text nodes / attributes)."""
    if s is None:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def strip_template_placeholders(pcf_text: str) -> str:
    """Remove any leftover ||| ... ||| placeholders."""
    return re.sub(r"\|\|\|.*?\|\|\|", "", pcf_text, flags=re.S)


def normalize_label(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def join_lines_for_html(s: str) -> str:
    """
    Convert multi-line plain text to XML-safe HTML with <br/>.
    Used for Office Hours / Location placeholders.
    """
    if not s:
        return ""
    lines = [xml_escape(ln.strip()) for ln in s.splitlines() if ln.strip()]
    return "<br/>".join(lines)


# -----------------------
# Parse WordPress HTML (including contact fields)
# -----------------------
def extract_contact_fields(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Tries multiple common WP patterns to extract:
      email, phone, fax, mail_code, office_hours, location_block
    """
    out = {
        "email": "",
        "phone": "",
        "fax": "",
        "mail_code": "",
        "office_hours": "",
        "location_block": "",
    }

    # 1) mailto/tel links
    a_email = soup.select_one('a[href^="mailto:"]')
    if a_email:
        out["email"] = (a_email.get("href") or "").replace("mailto:", "").strip()

    a_tel = soup.select_one('a[href^="tel:"]')
    if a_tel:
        out["phone"] = (a_tel.get("href") or "").replace("tel:", "").strip()

    # 2) Definition list <dt>Label</dt><dd>Value</dd>
    for dl in soup.find_all("dl"):
        dts = dl.find_all("dt")
        for dt in dts:
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

    # 3) Label + value in text blocks (fallback scan)
    page_text = soup.get_text("\n", strip=True)

    def find_multiline_block(label_variants: List[str]) -> str:
        # capture from label line until next known label line or end
        label_union = r"(email|e-mail|phone|telephone|contact|fax|mail code|mailcode|office hours|hours|location|address)"
        for lab in label_variants:
            m = re.search(
                rf"(?im)^{re.escape(lab)}\s*:?\s*$\n(.*?)(?=^\s*{label_union}\s*:?\s*$|\Z)",
                page_text,
                flags=re.S,
            )
            if m:
                return "\n".join([ln.strip() for ln in m.group(1).splitlines() if ln.strip()])
        return ""

    def find_singleline(label_variants: List[str]) -> str:
        for lab in label_variants:
            m = re.search(rf"(?im)^{re.escape(lab)}\s*:\s*(.+)$", page_text)
            if m:
                return m.group(1).strip()
        return ""

    if not out["email"]:
        out["email"] = find_singleline(["Email", "E-mail", "email", "e-mail"])

    if not out["phone"]:
        out["phone"] = find_singleline(["Phone", "Telephone", "Contact", "Phone Number", "phone", "telephone", "contact"])

    if not out["fax"]:
        out["fax"] = find_singleline(["Fax", "fax"])

    if not out["mail_code"]:
        out["mail_code"] = find_singleline(["Mail Code", "MailCode", "mail code", "mailcode"])

    if not out["office_hours"]:
        out["office_hours"] = find_multiline_block(["Office Hours", "office hours", "Hours", "hours"])

    if not out["location_block"]:
        out["location_block"] = find_multiline_block(["Location", "location", "Address", "address"])

    # 4) last resort phone regex if still empty
    if not out["phone"]:
        m = re.search(r"\b(\d{3}[-.\s]\d{3}[-.\s]\d{4})\b", soup.get_text(" ", strip=True))
        if m:
            out["phone"] = m.group(1)

    return out


def parse_wp_profile(html_text: str) -> Dict:
    """
    Parses WP markup similar to your autumn_askew.html.
    Missing fields return "" (blank).
    """
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

    # Header fields
    heading = soup.select_one(".faculty__heading")
    pronouns = title = program = department = region = ""

    if heading:
        p_tags = heading.find_all("p")

        # Pronouns line
        if len(p_tags) >= 1:
            p0 = p_tags[0].get_text(" ", strip=True)
            m = re.search(r"Pronouns:\s*(.+)$", p0)
            pronouns = text_or_empty(m.group(1) if m else "")

        # Title block
        if len(p_tags) >= 3:
            lines = [text_or_empty(x) for x in p_tags[2].stripped_strings]
            title = " | ".join([ln for ln in lines if ln])

        # Program / department
        if len(p_tags) >= 4:
            strong = p_tags[3].find("strong")
            program = text_or_empty(strong.get_text(" ", strip=True) if strong else "")
            strings = [text_or_empty(s) for s in p_tags[3].stripped_strings]
            if program and strings and strings[0] == program:
                strings = strings[1:]
            department = " | ".join([s for s in strings if s])

        # Region
        if len(p_tags) >= 5:
            region = text_or_empty(p_tags[4].get_text(" ", strip=True))

    # Office hours (original selector)
    office_hours = ""
    office = soup.select_one("#hours .faculty__available")
    if office:
        office_hours = text_or_empty(office.get_text("\n", strip=True))

    # Research, bio, mentors
    research = ""
    r = soup.select_one(".content-expertise p")
    if r:
        research = text_or_empty(r.get_text(" ", strip=True))

    bio = ""
    b = soup.select_one(".content-bio p")
    if b:
        bio = text_or_empty(b.get_text(" ", strip=True))

    mentors_html = ""
    mentors_p = soup.select_one(".content-messages p")
    if mentors_p:
        # may include <a> tags; keep tags, but make & XML-safe later
        mentors_html = mentors_p.decode_contents().strip()

    # Publications
    pub_items = [
        li.get_text(" ", strip=True)
        for li in soup.select("#publications li.ea-profile-activity")
    ]
    publications = [text_or_empty(p) for p in pub_items if text_or_empty(p)]

    # Links
    links: List[Tuple[str, str]] = []
    for a in soup.select("#links a"):
        href = (a.get("href") or "").strip()
        label = text_or_empty(a.get_text(" ", strip=True)) or href
        if href:
            links.append((label, href))

    # Twitter/X
    twitter = ""
    tw = soup.select_one("#accounts a[href*='twitter.com']")
    if tw:
        twitter = (tw.get("href") or "").strip()

    # Contact fields from WP
    contact = extract_contact_fields(soup)

    # Prefer #hours selector if found; otherwise use contact office hours
    office_hours_final = office_hours or contact.get("office_hours", "")

    return {
        "full_name": full_name,
        "display_name": name_part or full_name,
        "first_name": first,
        "last_name": last,
        "suffix": suffix,
        "pronouns": pronouns,
        "title": title,
        "program": program,
        "department": department,
        "region": region,
        "image_src": img_src,
        "image_alt": img_alt,
        "office_hours": office_hours_final,
        "research": research,
        "bio": bio,
        "mentors_html": mentors_html,
        "publications": publications,
        "links": links,
        "twitter": twitter,
        # contact
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
        "fax": contact.get("fax", ""),
        "mail_code": contact.get("mail_code", ""),
        "location_block": contact.get("location_block", ""),
    }


# -----------------------
# Template filling (OUC + |||...||| placeholders)
# -----------------------
def replace_metadata_title(pcf: str, new_title: str) -> str:
    pattern = r'(<ouc:properties\s+label="metadata">.*?<title>)(.*?)(</title>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf
    return re.sub(
        pattern,
        lambda m: m.group(1) + xml_escape(new_title) + m.group(3),
        pcf,
        flags=re.S,
    )


def replace_ouc_div_text(pcf: str, label: str, value: str) -> str:
    """
    Replace text inside:
      <ouc:div label="X"...><ouc:multiedit .../>VALUE</ouc:div>
    If the label doesn't exist in template, do nothing.
    """
    pattern = rf'(<ouc:div\s+label="{re.escape(label)}"[^>]*>\s*<ouc:multiedit[^>]*/>)(.*?)(</ouc:div>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf
    return re.sub(
        pattern,
        lambda m: m.group(1) + xml_escape(value or "") + m.group(3),
        pcf,
        flags=re.S,
    )


def replace_checkbox(pcf: str, label: str, checked: bool) -> str:
    """
    Replace checkbox value inside:
      <ouc:div label="show-xyz"...><ouc:multiedit type="checkbox" .../>true|false</ouc:div>
    If not present in template, do nothing.
    """
    pattern = rf'(<ouc:div\s+label="{re.escape(label)}"[^>]*>\s*<ouc:multiedit[^>]*/>)(.*?)(</ouc:div>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf
    val = "true" if checked else "false"
    return re.sub(pattern, lambda m: m.group(1) + val + m.group(3), pcf, flags=re.S)


def replace_image(pcf: str, src: str, alt: str) -> str:
    """
    Update <img ...> inside <ouc:div label="image"...>
    If image region doesn't exist, do nothing.
    """
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
    """
    Replace content after <ouc:editor .../> inside:
      <ouc:div label="bio"...><ouc:editor .../> ... </ouc:div>
    If not present in template, do nothing.
    """
    pattern = rf'(<ouc:div\s+label="{re.escape(label)}"[^>]*>.*?<ouc:editor[^>]*/>)(.*?)(</ouc:div>)'
    if not re.search(pattern, pcf, flags=re.S):
        return pcf

    def repl(m):
        html = (inner_html or "").strip()
        if html:
            return m.group(1) + "\n" + html + "\n    " + m.group(3)
        return m.group(1) + "\n    " + m.group(3)

    return re.sub(pattern, repl, pcf, flags=re.S)


def replace_triplebar_placeholders(pcf: str, data: Dict) -> str:
    """
    Replace template placeholders like:
      ||| E-mail |||
      ||| Phone |||
    using PLACEHOLDER_TO_KEY mapping.

    If placeholder label isn't in mapping => blank it.
    If mapped value missing => blank it.
    """
    pattern = r"\|\|\|\s*(.*?)\s*\|\|\|"

    def repl(m: re.Match) -> str:
        token = (m.group(1) or "").strip()
        key = PLACEHOLDER_TO_KEY.get(token)
        if not key:
            return ""
        val = data.get(key, "") or ""
        # Multi-line friendly output for some blocks
        if key in {"office_hours", "location_block"}:
            return join_lines_for_html(val)
        return xml_escape(val)

    return re.sub(pattern, repl, pcf)


def build_ul(items: List[str]) -> str:
    if not items:
        return ""
    lis = "\n".join([f"  <li>{xml_escape(it)}</li>" for it in items])
    return "<ul>\n" + lis + "\n</ul>"


def build_other_details_html(data: Dict) -> str:
    bits: List[str] = []
    if data.get("links"):
        bits.append("<h3>Links</h3>")
        bits.append("<ul>")
        for label, href in data["links"]:
            bits.append(f'  <li><a href="{xml_escape(href)}">{xml_escape(label)}</a></li>')
        bits.append("</ul>")
    if data.get("twitter"):
        bits.append("<h3>Accounts</h3>")
        bits.append(f'<p><a href="{xml_escape(data["twitter"])}">X (Twitter)</a></p>')
    return "\n".join(bits).strip()


def apply_show_flags(pcf: str, data: Dict) -> str:
    """
    If your template has show-* checkbox fields, we will hide sections when blank.
    If the template does NOT have these labels, this does nothing (safe).
    """
    pcf = replace_checkbox(pcf, "show-pronouns", bool(data.get("pronouns")))
    pcf = replace_checkbox(pcf, "show-region", bool(data.get("region")))
    pcf = replace_checkbox(pcf, "show-office-hours", bool(data.get("office_hours")))
    pcf = replace_checkbox(pcf, "show-research", bool(data.get("research")))
    pcf = replace_checkbox(pcf, "show-mentors", bool(data.get("mentors_html")))
    pcf = replace_checkbox(pcf, "show-publications", bool(data.get("publications")))
    pcf = replace_checkbox(
        pcf, "show-other-details", bool(data.get("links") or data.get("twitter"))
    )
    pcf = replace_checkbox(pcf, "show-image", bool(data.get("image_src") or data.get("image_alt")))
    return pcf


def html_to_pcf(html_path: Path, template_text: str) -> Tuple[str, str]:
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    data = parse_wp_profile(html_text)

    pcf = template_text

    # Title
    title = data.get("display_name") or data.get("full_name") or html_path.stem
    pcf = replace_metadata_title(pcf, title)

    # Text fields (blank if missing)
    pcf = replace_ouc_div_text(pcf, "first-name", data.get("first_name", ""))
    pcf = replace_ouc_div_text(pcf, "last-name", data.get("last_name", ""))
    pcf = replace_ouc_div_text(pcf, "suffix", data.get("suffix", ""))
    pcf = replace_ouc_div_text(pcf, "pronouns", data.get("pronouns", ""))
    pcf = replace_ouc_div_text(pcf, "title", data.get("title", ""))
    pcf = replace_ouc_div_text(pcf, "program", data.get("program", ""))
    pcf = replace_ouc_div_text(pcf, "department", data.get("department", ""))
    pcf = replace_ouc_div_text(pcf, "region", data.get("region", ""))  # safe if label not present

    # Image
    pcf = replace_image(pcf, data.get("image_src", ""), data.get("image_alt", ""))

    # WYSIWYG regions (blank if missing)
    bio = data.get("bio", "")
    office = data.get("office_hours", "")
    research = data.get("research", "")

    pcf = replace_ouc_editor_region(pcf, "bio", f"<p>{xml_escape(bio)}</p>" if bio else "")
    # preserve line breaks for office hours
    pcf = replace_ouc_editor_region(
        pcf, "office-hours", f"<p>{join_lines_for_html(office)}</p>" if office else ""
    )
    pcf = replace_ouc_editor_region(
        pcf, "research", f"<p>{xml_escape(research)}</p>" if research else ""
    )

    mentors_html = data.get("mentors_html", "")
    if mentors_html:
        # keep tags but make & safe
        mentors_safe = mentors_html.replace("&", "&amp;")
        pcf = replace_ouc_editor_region(pcf, "mentors", f"<p>{mentors_safe}</p>")
    else:
        pcf = replace_ouc_editor_region(pcf, "mentors", "")

    pubs_html = build_ul(data.get("publications", []))
    pcf = replace_ouc_editor_region(pcf, "publications", pubs_html)

    other = build_other_details_html(data)
    pcf = replace_ouc_editor_region(pcf, "other-details", other if other else "")

    # Hide sections when blank (only if your template supports show-* labels)
    pcf = apply_show_flags(pcf, data)

    # ✅ Replace ||| ... ||| placeholders using WP contact values
    pcf = replace_triplebar_placeholders(pcf, data)

    # IMPORTANT: remove any leftover |||...||| placeholders (blank them)
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

    # de-dupe (preserve order)
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
            "Usage:\n"
            "  python wp_to_pcfmult.py <html_or_folder> [more_html_or_folders...] <template-pcfGen.txt>\n",
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