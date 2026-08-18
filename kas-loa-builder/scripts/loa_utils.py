"""
LOA Excel column utilities — reusable helpers for openpyxl manipulations.

Usage:
    from loa_utils import adjust_merged_ranges_after_delete_cols, col_letter_to_num, col_num_to_letter

    # After ws.delete_cols(start, count):
    adjust_merged_ranges_after_delete_cols(ws, deleted_start_col=6, deleted_count=2)
"""

import re


def col_letter_to_num(letters: str) -> int:
    """'A' -> 1, 'Z' -> 26, 'AA' -> 27"""
    num = 0
    for ch in letters.upper():
        num = num * 26 + (ord(ch) - ord('A') + 1)
    return num


def col_num_to_letter(num: int) -> str:
    """1 -> 'A', 26 -> 'Z', 27 -> 'AA'"""
    result = ''
    while num > 0:
        num, rem = divmod(num - 1, 26)
        result = chr(ord('A') + rem) + result
    return result


def adjust_range_str(rng_str: str, deleted_start_col: int, deleted_count: int) -> str | None:
    """
    Adjust an Excel range string after deleting columns.

    Columns >= deleted_start_col shift left by deleted_count.
    Returns None if the range becomes invalid (fully inside deleted zone).

    Example:
        adjust_range_str('F1:H1', 6, 2) -> 'D1:F1'  (F->D, H->F)
        adjust_range_str('A1:A2', 6, 2) -> 'A1:A2'   (unchanged)
        adjust_range_str('F1:G1', 6, 2) -> None       (fully deleted)
    """
    m = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', rng_str)
    if not m:
        return rng_str

    c1_num = col_letter_to_num(m.group(1))
    c2_num = col_letter_to_num(m.group(3))
    r1 = int(m.group(2))
    r2 = int(m.group(4))

    # Shift columns that are >= deleted_start_col
    if c1_num >= deleted_start_col:
        c1_num -= deleted_count
    if c2_num >= deleted_start_col:
        c2_num -= deleted_count

    if c1_num < 1 or c2_num < 1:
        return None
    if c1_num > c2_num:
        return None

    return f"{col_num_to_letter(c1_num)}{r1}:{col_num_to_letter(c2_num)}{r2}"


def adjust_merged_ranges_after_delete_cols(ws, deleted_start_col: int, deleted_count: int) -> int:
    """
    Clear and rebuild all merged cell ranges after column deletion.

    Call this AFTER ws.delete_cols(deleted_start_col, deleted_count).

    Args:
        ws: openpyxl worksheet
        deleted_start_col: 1-based column number where deletion started
        deleted_count: number of columns deleted

    Returns:
        Number of merged ranges successfully re-applied.
    """
    old_ranges = [str(m) for m in ws.merged_cells.ranges]
    ws.merged_cells.ranges.clear()

    applied = 0
    for old_rng in old_ranges:
        new_rng = adjust_range_str(old_rng, deleted_start_col, deleted_count)
        if new_rng:
            try:
                ws.merge_cells(new_rng)
                applied += 1
            except Exception:
                pass  # skip ranges that became invalid

    return applied


def merge_authority_values(ws, from_cols: list[int], to_col: int):
    """
    Merge authority values (R, A, R/A) from multiple columns into one.

    Example: merge Excom(6), BOD(7) into Shareholder(8):
        merge_authority_values(ws, [6, 7], 8)

    Non-None values are joined with ' / ' separator.
    Duplicates are removed.
    """
    for row in range(1, ws.max_row + 1):
        vals = []
        for col in from_cols:
            v = ws.cell(row=row, column=col).value
            if v is not None and str(v).strip():
                sv = str(v).strip()
                if sv not in vals:
                    vals.append(sv)

        target = ws.cell(row=row, column=to_col)
        existing = target.value
        if existing is not None and str(existing).strip():
            ev = str(existing).strip()
            if ev not in vals:
                vals.append(ev)

        if vals:
            target.value = ' / '.join(vals)
