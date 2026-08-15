#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KAS Skills Manager — ติดตั้ง/อัปเดต/ถอน skills อัตโนมัติ พร้อม version control

พฤติกรรม (ตามข้อกำหนด):
  1. สแกน skills เดิมในเครื่อง + เทียบ version กับ repo
  2. skill ตัวเก่า → อัปเดตเป็น version ล่าสุด (KAS + OKAS)
  3. skill ที่ไม่เคยลง → ลงตัวล่าสุดให้
  4. skill ใน deprecated list (xkas-* + ชื่อเก่า kas-*) → ถอน/ลบออก
  5. skill ที่อยู่ path ผิด (nested เก่า) → ย้ายกลับมา flat หรือลบ duplicate
  6. รายงาน: ลง/อัปเดต/ถอน/ย้าย/ข้าม/ปัญหา

Usage:
  python skill_manager.py <repo_dir> [--dry-run]
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ---------- Config ที่ต้องตั้งให้ทุกเครื่อง ----------
CONFIG_KEYS = [
    ("model.provider", "opencode-go"),
    ("model.default", "deepseek-v4-pro"),
    ("moa.enabled", "false"),
    ("auxiliary.vision.provider", "gemini"),
    ("auxiliary.vision.model", "gemini-3.6-flash"),
    ("auxiliary.web_extract.provider", "opencode-go"),
    ("auxiliary.web_extract.model", "deepseek-v4-pro"),
    ("delegation.provider", "opencode-go"),
    ("delegation.model", "deepseek-v4-pro"),
]

TELEGRAM_ADMIN_ID = "8702982867"


def skills_root() -> Path:
    if os.name == "nt":
        return Path.home() / "AppData" / "Local" / "hermes" / "skills"
    return Path.home() / ".hermes" / "skills"


def load_manifest(repo_dir: Path) -> dict:
    p = repo_dir / "skills_manifest.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"approved_kas": [], "deprecated": []}


def read_frontmatter(skill_md: Path) -> dict:
    """Parse SKILL.md frontmatter → dict (name/version/...). {} ถ้าไม่มี."""
    try:
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {}
    m = re.match(r"\A---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


def parse_version(v: str) -> tuple:
    """'5.0.0' → (5,0,0). ขาด/ว่าง → (0,0,0)."""
    nums = re.findall(r"\d+", v or "")
    parts = [int(n) for n in (nums[:3] + ["0", "0", "0"])[:3]]
    return tuple(parts)


def find_skill_dirs(root: Path) -> list:
    """Walk root → list dirs ที่มี SKILL.md (ทุกระดับชั้น)."""
    result = []
    if not root.exists():
        return result
    for dirpath, dirnames, filenames in os.walk(root):
        if "SKILL.md" in filenames:
            result.append(Path(dirpath))
    return result


def scan_local(root: Path) -> dict:
    """{skill_name: [{"dir", "version"}, ...]} — 1 ชื่ออาจมีหลาย path (nested เดิม)."""
    skills = {}
    for d in find_skill_dirs(root):
        fm = read_frontmatter(d / "SKILL.md")
        name = fm.get("name", "")
        if not name:
            continue
        skills.setdefault(name, []).append({"dir": d, "version": fm.get("version", "")})
    return skills


def scan_repo(repo_dir: Path, manifest: dict) -> dict:
    """{skill_name: {"dir", "version"}} เฉพาะ approved (okas-* + approved_kas)."""
    root = Path(repo_dir)
    approved = {}
    approved_kas = set(manifest.get("approved_kas", []))
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        if not (d / "SKILL.md").exists():
            continue
        if d.name.startswith("okas-") or d.name in approved_kas:
            fm = read_frontmatter(d / "SKILL.md")
            name = fm.get("name", d.name)
            approved[name] = {"dir": d, "version": fm.get("version", "")}
    return approved


def _install(flat: Path, src: Path) -> None:
    if flat.exists():
        shutil.rmtree(flat)
    shutil.copytree(src, flat, ignore=shutil.ignore_patterns(".git"))


TEXT_EXTS = {".md", ".py", ".html", ".htm", ".json", ".txt", ".css", ".js",
             ".yaml", ".yml", ".bat", ".ps1", ".csv"}


def fix_paths(root: Path, dry_run: bool) -> int:
    """แทนที่ hardcoded path ของเครื่องพี่ (C:\\Users\\ASUS) → user home ปัจจุบัน."""
    home = str(Path.home())
    variants = ["C:\\Users\\ASUS", "C:/Users/ASUS"]
    fixed = 0
    if not root.exists():
        return 0
    for f in root.rglob("*"):
        if not f.is_file() or f.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        orig = text
        for v in variants:
            text = text.replace(v, home)
        if text != orig:
            if not dry_run:
                try:
                    f.write_text(text, encoding="utf-8")
                except Exception:
                    continue
            fixed += 1
    return fixed


def run_config_set(dry_run: bool) -> list:
    results = []
    for key, val in CONFIG_KEYS:
        if dry_run:
            results.append(f"[dry] hermes config set {key} {val}")
            continue
        try:
            r = subprocess.run(
                ["hermes", "config", "set", key, val],
                capture_output=True, text=True, timeout=60,
            )
            results.append(f"{'OK ' if r.returncode == 0 else 'ERR'} {key} = {val}")
        except Exception as e:
            results.append(f"ERR {key} ({e})")
    return results


def send_telegram(summary: str, dry_run: bool) -> None:
    if dry_run:
        print("  [dry-run] skip Telegram")
        return
    try:
        subprocess.run(
            ["hermes", "send", "--platform", "telegram", "--to", TELEGRAM_ADMIN_ID, summary],
            capture_output=True, text=True, timeout=60,
        )
    except Exception as e:
        print(f"  (Telegram send failed: {e})")


def main() -> None:
    repo_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    dry_run = "--dry-run" in sys.argv
    root = skills_root()
    manifest = load_manifest(repo_dir)
    repo_skills = scan_repo(repo_dir, manifest)
    local_skills = scan_local(root)
    deprecated = set(manifest.get("deprecated", []))

    installed, updated, removed, moved, skipped, errors = [], [], [], [], [], []

    def do_install(flat, src):
        try:
            _install(flat, src)
            return True
        except Exception as e:
            errors.append((name, f"install/update failed: {e}"))
            return False

    def drop_nonflat(name, local_dirs, flat):
        """ลบ dir ที่ไม่ใช่ flat (duplicate/nested เก่า)."""
        for d in local_dirs:
            p = d["dir"]
            if p == flat:
                continue
            if dry_run:
                removed.append((name, d["version"], "(dup, dry)"))
                continue
            try:
                if p.exists():
                    shutil.rmtree(p)
                    removed.append((name, d["version"], "dup"))
            except Exception as e:
                errors.append((name, f"dedupe failed: {e}"))

    # 1. ลงใหม่ / อัปเดต / ย้าย skills ที่ approved
    for name, info in sorted(repo_skills.items()):
        flat = root / name
        local_dirs = local_skills.get(name, [])
        rv = parse_version(info["version"])

        if not local_dirs:
            if dry_run:
                installed.append((name, info["version"], "(dry)"))
            elif do_install(flat, info["dir"]):
                installed.append((name, info["version"], ""))
            continue

        best = max(local_dirs, key=lambda d: parse_version(d["version"]))
        bv = parse_version(best["version"])

        if rv > bv:
            # repo ใหม่กว่า → อัปเดตลง flat + ลบ nested เก่า
            if dry_run:
                updated.append((name, best["version"], info["version"], "(dry)"))
            elif do_install(flat, info["dir"]):
                updated.append((name, best["version"], info["version"], ""))
            drop_nonflat(name, local_dirs, flat)
            continue

        # local >= repo → เก็บ local (ย้ายไป flat ถ้าอยู่ nested) + ลบ dup
        if best["dir"] != flat:
            if dry_run:
                moved.append((name, best["version"], "(dry)"))
            else:
                try:
                    if flat.exists():
                        shutil.rmtree(flat)
                        removed.append((name, "(old flat)", "replaced"))
                    shutil.move(str(best["dir"]), str(flat))
                    moved.append((name, best["version"], ""))
                except Exception as e:
                    errors.append((name, f"move failed: {e}"))
        drop_nonflat(name, [d for d in local_dirs if d["dir"] != best["dir"]], flat)
        if rv == bv:
            skipped.append((name, "already latest"))
        else:
            skipped.append((name, f"local {best['version']} > repo {info['version']}"))

    # 2. ถอน/ลบ deprecated skills (ทุกที่ใน tree)
    for name in sorted(deprecated):
        for d in local_skills.get(name, []):
            if dry_run:
                removed.append((name, d["version"], "(dry)"))
                continue
            try:
                shutil.rmtree(d["dir"])
                removed.append((name, d["version"], ""))
            except Exception as e:
                errors.append((name, f"remove failed: {e}"))

    # 2.5 แก้ hardcoded paths (C:\Users\ASUS → user home)
    path_fixed = fix_paths(root, dry_run)

    # 3. ตั้งค่า config
    config_results = run_config_set(dry_run)

    # 4. รายงาน
    print("=" * 62)
    print("  KAS Skills Manager — สรุปผลการติดตั้ง")
    print("=" * 62)
    print(f"\n✅ ติดตั้งใหม่  {len(installed)} ตัว")
    for n, v, note in installed:
        print(f"   + {n}  v{v}  {note}".rstrip())
    print(f"\n🔄 อัปเดต      {len(updated)} ตัว")
    for n, ov, nv, note in updated:
        print(f"   ↑ {n}  v{ov} → v{nv}  {note}".rstrip())
    print(f"\n🗂️  ย้ายตำแหน่ง {len(moved)} ตัว (nested → flat)")
    for n, v, note in moved:
        print(f"   ⇄ {n}  (v{v})  {note}".rstrip())
    print(f"\n🗑️  ถอน/ลบ     {len(removed)} ตัว")
    for n, v, note in removed:
        print(f"   - {n}  (v{v})  {note}".rstrip())
    print(f"\n⏭️  ข้าม        {len(skipped)} ตัว")
    for n, detail in skipped:
        print(f"   · {n}: {detail}")
    print(f"\n🔧 แก้ path        {path_fixed} ไฟล์")
    print(f"\n⚙️  Config ({len(config_results)} ค่า)")
    for r in config_results:
        print(f"   {r}")
    if errors:
        print(f"\n⚠️  พบปัญหา {len(errors)} รายการ:")
        for n, e in errors:
            print(f"   ✗ {n}: {e}")
    else:
        print("\n⚠️  ไม่พบปัญหาใด ๆ")
    print("\n" + "=" * 62)
    print("  เสร็จสิ้น — กรุณา restart Hermes หรือ /reload-skills")
    print("=" * 62)

    # 5. แจ้ง Admin ทาง Telegram
    summary = (
        f"🔔 KAS Skills Manager: ติดตั้ง {len(installed)} / อัปเดต {len(updated)} / "
        f"ย้าย {len(moved)} / ถอน {len(removed)} / ข้าม {len(skipped)}"
        + (f" / ⚠️ปัญหา {len(errors)}" if errors else "")
    )
    send_telegram(summary, dry_run)


if __name__ == "__main__":
    main()
