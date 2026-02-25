#!/usr/bin/env python3
"""
Convert a WordPress faculty-profile HTML export into an OU Campus PCF,
using an existing PCF (ex: carrie-house.pcf) as the template.

The generated PCF will be saved inside an "output" folder.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape


OUTPUT_DIR = Path("output")


def text_or_empty(x) -> str:
    return (x or "").strip()


def parse_wp_profile(html_text: str) -> dict:
    soup = BeautifulSoup(html_text, "html.parser")

    h1 = soup.find("h1")
    full_name = text_or_empty(h1.get_text(" ", strip=True) if h1 else "")

    name_part, suffix = full_name, ""
    if "," in full_name:
        name_part, suffix = [p.strip() for p in full_name.split(",", 1)]

    parts = name_part.split()
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) >= 2 else (parts[0] if parts else "")

    img = soup.select_one(".faculty__image img")
    img_src = img.get("src", "") if img else ""
    img_alt = img.get("alt", "") if img else ""

    heading = soup.select_one(".faculty__heading")
    pronouns = title = program = department = region = ""

    if heading:
        p_tags = heading.find_all("p")

        if len(p_tags) >= 1:
            p0 = p_tags[0].get_text(" ", strip=True)
            m = re.search(r"Pronouns:\s*(.+)$", p0)
            pronouns = text_or_empty(m.group(1) if m else p0)

        if len(p_tags) >= 3:
            lines = [text_or_empty(x) for x in p_tags[2].stripped_strings]
            title = " | ".join([ln for ln in lines if ln])

        if len(p_tags) >= 4:
            strong = p_tags[3].find("strong")
            program = text_or_empty(strong.get_text(" ", strip=True) if strong else "")
            strings = [text_or_empty(s) for s in p_tags[3].stripped_strings]
            if program and strings and strings[0] == program:
                strings = strings[1:]
            department = " | ".join([s for s in strings if s])

        if len(p_tags) >= 5:
            region = text_or_empty(p_tags[4].get_text(" ", strip=True))

    office_hours = ""
    office = soup.select_one("#hours .faculty__available")
    if office:
        office_hours = text_or_empty(office.get_text(" ", strip=True))

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
        mentors_html = mentors_p.decode_contents().strip()

    pub_items = [
        li.get_text(" ", strip=True)
        for li in soup.select("#publications li.ea-profile-activity")
    ]
    pub_items = [text_or_empty(p) for p in pub_items if text_or_empty(p)]

    return {
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
        "office_hours": office_hours,
        "research": research,
        "bio": bio,
        "mentors_html": mentors_html,
        "publications": pub_items,
    }


def replace_metadata_title(pcf: str, new_title: str) -> str:
    pattern = r'(<ouc:properties\s+label="metadata">.*?<title>)(.*?)(</title>)'
    return re.sub(pattern, lambda m: m.group(1) + escape(new_title) + m.group(3), pcf, flags=re.S)


def replace_ouc_div_text(pcf: str, label: str, value: str) -> str:
    pattern = rf'(<ouc:div\s+label="{re.escape(label)}"[^>]*>\s*<ouc:multiedit[^>]*/>)(.*?)(</ouc:div>)'
    return re.sub(pattern, lambda m: m.group(1) + escape(value) + m.group(3), pcf, flags=re.S)


def replace_ouc_div_editor_html(pcf: str, label: str, inner_html: str) -> str:
    pattern = rf'(<ouc:div\s+label="{re.escape(label)}"[^>]*>.*?<ouc:editor[^>]*/>)(.*?)(</ouc:div>)'

    def repl(m):
        html = inner_html.strip()
        return m.group(1) + ("\n" + html + "\n    " if html else "\n    ") + m.group(3)

    return re.sub(pattern, repl, pcf, flags=re.S)


def replace_image(pcf: str, src: str, alt: str) -> str:
    pattern = r'(<ouc:div\s+label="image"[^>]*>.*?<img\b)([^>]*)(>)'

    def repl(m):
        attrs = m.group(2)
        attrs = re.sub(r'\bsrc="[^"]*"', f'src="{escape(src)}"', attrs)
        attrs = re.sub(r'\balt="[^"]*"', f'alt="{escape(alt)}"', attrs)
        return m.group(1) + attrs + m.group(3)

    return re.sub(pattern, repl, pcf, flags=re.S)


def build_ul(items):
    if not items:
        return ""
    lis = "\n".join([f"  <li>{escape(it)}</li>" for it in items])
    return "<ul>\n" + lis + "\n</ul>"


def wp_html_to_pcf(input_html: Path, base_pcf: Path) -> Path:
    html_text = input_html.read_text(encoding="utf-8", errors="ignore")
    pcf_text = base_pcf.read_text(encoding="utf-8", errors="ignore")

    data = parse_wp_profile(html_text)

    pcf_text = replace_metadata_title(pcf_text, data["display_name"])
    pcf_text = replace_ouc_div_text(pcf_text, "first-name", data["first_name"])
    pcf_text = replace_ouc_div_text(pcf_text, "last-name", data["last_name"])
    pcf_text = replace_ouc_div_text(pcf_text, "suffix", data["suffix"])
    pcf_text = replace_ouc_div_text(pcf_text, "pronouns", data["pronouns"])
    pcf_text = replace_ouc_div_text(pcf_text, "title", data["title"])
    pcf_text = replace_ouc_div_text(pcf_text, "program", data["program"])
    pcf_text = replace_ouc_div_text(pcf_text, "department", data["department"])

    pcf_text = replace_image(pcf_text, data["image_src"], data["image_alt"])

    pcf_text = replace_ouc_div_editor_html(
        pcf_text, "bio", f"<p>{escape(data['bio'])}</p>" if data["bio"] else ""
    )
    pcf_text = replace_ouc_div_editor_html(
        pcf_text,
        "office-hours",
        f"<p>{escape(data['office_hours'])}</p>" if data["office_hours"] else "",
    )
    pcf_text = replace_ouc_div_editor_html(
        pcf_text, "research", f"<p>{escape(data['research'])}</p>" if data["research"] else ""
    )
    pcf_text = replace_ouc_div_editor_html(
        pcf_text, "publications", build_ul(data["publications"])
    )

    # Ensure output folder exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    output_path = OUTPUT_DIR / f"{data['first_name'].lower()}-{data['last_name'].lower()}.pcf"
    output_path.write_text(pcf_text, encoding="utf-8")

    return output_path


def main(argv):
    if len(argv) != 3:
        print("Usage: python wp_to_pcf.py input.html base.pcf")
        return 2

    input_html = Path(argv[1])
    base_pcf = Path(argv[2])

    output_path = wp_html_to_pcf(input_html, base_pcf)
    print(f"Wrote: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))