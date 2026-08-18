#!/usr/bin/env python3
"""
Generate interactive RCM (Risk Control Matrix) HTML from normalized JSON.

Cross-platform: uses pathlib + relative paths only. No hardcoded user paths.
Python 3.8+ required. Stdlib only (json, pathlib, html, argparse, datetime).

Usage:
    python generate_rcm.py rcm_data.json
    python generate_rcm.py rcm_data.json -o RCM_MyClient.html

Input JSON schema — see templates/sample_input.json
"""
import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "rcm_template.html"


def esc(text: str) -> str:
    """Escape text for safe HTML attribute / text insertion."""
    return html.escape(str(text), quote=True)


def esc_attr(text: str) -> str:
    """Escape text for use inside an HTML attribute (already quoted)."""
    return esc(text).replace("\n", " ").replace("\r", " ")


def _join(items, sep="\n"):
    """Join a list of strings with a separator; return '' if empty."""
    if not items:
        return ""
    return sep.join(str(x) for x in items)


def build_control_select() -> str:
    """Return the <select> element for the control-level column (col 11)."""
    options = [
        ("", "-- เลือกระดับ --"),
        ("Ad-hoc", "Ad-hoc — ไม่มีการควบคุมภายในที่เป็นมาตรฐาน"),
        ("Developing", "Developing — มีกระบวนการแต่ขาดความสม่ำเสมอ"),
        ("Standard", "Standard — มีกระบวนการมาตรฐาน มีการวัดและปรับปรุง"),
        ("Leading", "Leading — มาตรฐานระดับสากลหรือผู้นำอุตสาหกรรม"),
    ]
    opts = "".join(
        f'<option value="{v}">{esc(label)}</option>' for v, label in options
    )
    return (
        f'<select class="control-level" onchange="updateControlLevel(this)" '
        f'style="width:100%;padding:4px;border-radius:4px;border:1px solid #ccc;'
        f'font-family:Sarabun,sans-serif;font-size:12px;">{opts}</select>'
    )


def build_row(row: dict, idx: int, proc: str, act_code: str, first_of_activity: bool, rowspan: int, act_full_name: str) -> str:
    """Build a single <tr> for a control row."""
    risk = esc(row.get("risk", ""))
    control = esc(row.get("control", ""))
    policy = esc(_join(row.get("policy", [])))
    procedure = esc(_join(row.get("procedure", [])))
    kri = esc(row.get("kri", ""))
    test = esc(_join(row.get("test", [])))
    report = esc(row.get("report", ""))
    question = esc(row.get("question", ""))

    attrs = (
        f' data-proc="{esc_attr(proc)}"'
        f' data-act="{esc_attr(act_code)}"'
        f' data-risk="{esc_attr(row.get("risk", ""))}"'
        f' data-ctrl="{esc_attr(row.get("control", ""))}"'
        f' data-test="{esc_attr(_join(row.get("test", []), " "))}"'
    )

    # Activity cell (col 1) only on first row of each activity, with rowspan
    if first_of_activity:
        act_cell = (
            f'<td data-col="1" rowspan="{rowspan}" class="act-merge" contenteditable="true">'
            f'{esc(act_full_name)}</td>'
        )
    else:
        act_cell = ""

    num_style = 'style="text-align:center;color:#9e9e9e;font-size:11px;"'
    select = build_control_select()

    return (
        f'<tr{attrs}>'
        f'<td data-col="0" {num_style}>{idx}</td>'
        f'{act_cell}'
        f'<td data-col="2" contenteditable="true">{risk}</td>'
        f'<td data-col="3" contenteditable="true">{control}</td>'
        f'<td data-col="4" contenteditable="true" style="font-size:12px;">{policy}</td>'
        f'<td data-col="5" contenteditable="true" style="font-size:12px;">{procedure}</td>'
        f'<td data-col="6" contenteditable="true" style="font-size:12px;">{kri}</td>'
        f'<td data-col="7" contenteditable="true">{test}</td>'
        f'<td data-col="8" contenteditable="true" style="font-size:12px;">{report}</td>'
        f'<td data-col="9" contenteditable="true">{question}</td>'
        f'<td data-col="10" contenteditable="true"></td>'
        f'<td data-col="11">{select}</td>'
        f'<td data-col="12" contenteditable="true"></td>'
        f'</tr>'
    )


def build_panel(process: dict) -> str:
    """Build a .process-panel div for one process."""
    code = process["code"]
    label = process.get("label", f"Process {code}")
    activities = process.get("activities", [])

    rows_html = []
    row_counter = 0
    for activity in activities:
        act_code = activity.get("code", "")
        act_name = activity.get("name", act_code)
        full_name = f"{act_code}: {act_name}" if act_name else act_code
        rows = activity.get("rows", [])
        rowspan = len(rows)
        for i, row in enumerate(rows):
            row_counter += 1
            rows_html.append(
                build_row(
                    row, row_counter, code, act_code,
                    first_of_activity=(i == 0),
                    rowspan=rowspan,
                    act_full_name=full_name,
                )
            )

    # Column headers (13 columns, matching the template)
    col_names = [
        "#", "กิจกรรม", "ความเสี่ยง", "การควบคุมที่ควรมี", "Policy", "Procedure",
        "KRI", "วิธีการตรวจสอบ", "Report", "คำถามสัมภาษณ์",
        "การควบคุมที่มีอยู่จริง", "ระดับการควบคุมภายใน", "หน่วยงานที่รับผิดชอบ",
    ]
    th_cells = "".join(
        f'<th data-col="{i}">{esc(name)}'
        f'<span class="resize-handle" onmousedown="startResize(event,this)"></span></th>'
        for i, name in enumerate(col_names)
    )

    total = len(rows_html)
    n_activities = len(activities)

    active_cls = " active" if process.get("default_active", False) else ""
    return (
        f'<div class="process-panel{active_cls}" id="panel-{code}">'
        f'<div class="panel-header"><span>{esc(label)} — {n_activities} กิจกรรม</span>'
        f'<span class="stats">{total} รายการควบคุม</span></div>'
        f'<div class="scroll-outer"><table class="rcm">'
        f'<thead><tr>{th_cells}</tr></thead>'
        f'<tbody>{"".join(rows_html)}</tbody>'
        f'</table></div></div>'
    )


def build_tabs(processes) -> str:
    """Build the sheet-tabs HTML."""
    tabs = []
    for process in processes:
        code = process["code"]
        label = process.get("label", f"Process {code}")
        total = sum(len(a.get("rows", [])) for a in process.get("activities", []))
        active = ' active' if process.get("default_active", False) else ''
        tabs.append(
            f'<div class="sheet-tab{active}" onclick="switchProcess(\'{esc_attr(code)}\')" data-proc="{esc_attr(code)}">'
            f'{esc(label)} <span class="badge">{total}</span></div>'
        )
    return "".join(tabs)


def build_col_menu() -> str:
    """Build the column-toggle menu (3 mandatory + 10 toggleable)."""
    names = [
        "#", "กิจกรรม", "ความเสี่ยง", "การควบคุมที่ควรมี", "Policy", "Procedure",
        "KRI", "วิธีการตรวจสอบ", "Report", "คำถามสัมภาษณ์",
        "การควบคุมที่มีอยู่จริง", "ระดับการควบคุมภายใน", "หน่วยงานที่รับผิดชอบ",
    ]
    labels = []
    for i, name in enumerate(names):
        if i in (0, 1, 2):
            labels.append(
                f'<label class="mandatory"><input type="checkbox" onchange="toggleCol({i},this)" checked disabled> {esc(name)} 🔒</label>'
            )
        else:
            labels.append(
                f'<label><input type="checkbox" onchange="toggleCol({i},this)" checked> {esc(name)}</label>'
            )
    return "".join(labels)


def main():
    parser = argparse.ArgumentParser(description="Generate interactive RCM HTML")
    parser.add_argument("input", help="Path to normalized JSON data file")
    parser.add_argument("-o", "--output", help="Output HTML path (default: RCM_<client>_<date>.html)")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: input file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    with open(in_path, encoding="utf-8") as f:
        data = json.load(f)

    client = data.get("client_name", "Client")
    processes = data.get("processes", [])

    if not processes:
        print("ERROR: 'processes' is empty", file=sys.stderr)
        sys.exit(1)

    # Set default active = first process
    for i, p in enumerate(processes):
        p["default_active"] = p.get("default_active", i == 0)

    total_controls = sum(
        len(a.get("rows", [])) for p in processes for a in p.get("activities", [])
    )

    # Read template
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template = f.read()

    meta_html = (
        f"<div>{esc(data.get('db_version', 'RCM Database'))}</div>"
        f"<div>Generated: {datetime.now().strftime('%d/%m/%Y %H:%M')} | {total_controls} controls</div>"
    )

    process_order = "[" + ",".join(f'"{p["code"]}"' for p in processes) + "]"

    html_out = (
        template
        .replace("{{CLIENT_NAME}}", esc(client))
        .replace("{{META_HTML}}", meta_html)
        .replace("{{PROCESS_TABS}}", build_tabs(processes))
        .replace("{{PROCESS_PANELS}}", "".join(build_panel(p) for p in processes))
        .replace("{{COL_MENU_HTML}}", build_col_menu())
        .replace("{{TOTAL}}", str(total_controls))
        .replace("{{PROCESS_ORDER}}", process_order)
    )

    # Output path
    if args.output:
        out_path = Path(args.output)
    else:
        safe_client = "".join(c if c.isalnum() else "_" for c in client)
        out_path = Path(f"RCM_{safe_client}_{datetime.now().strftime('%d%m%Y')}.html")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    print(f"✅ Generated: {out_path}")
    print(f"   Processes: {len(processes)} | Activities: {sum(len(p.get('activities', [])) for p in processes)} | Controls: {total_controls}")


if __name__ == "__main__":
    main()
