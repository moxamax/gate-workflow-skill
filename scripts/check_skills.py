#!/usr/bin/env python3
"""檢查 skills/ 的 frontmatter、SKILL.md body 大小與相對連結。只用標準函式庫。"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
# Antigravity 的 skill body 上限；超過時把細節移到 references/ 並以明確指引讀取。
BODY_LIMIT = 24_000
LINK = re.compile(r"\]\(([^)\s]+)\)")


def check_skill(skill_md: pathlib.Path) -> list[str]:
    text = skill_md.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if not text.startswith("---") or len(parts) < 3:
        return [f"{skill_md}: 缺少 frontmatter"]
    errors = []
    front, body = parts[1], parts[2].strip()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    if not name or name.group(1).strip() != skill_md.parent.name:
        errors.append(f"{skill_md}: frontmatter name 必須等於目錄名稱 {skill_md.parent.name}")
    if not re.search(r"^description:\s*\S", front, re.M):
        errors.append(f"{skill_md}: 缺少 description")
    size = len(body.encode("utf-8"))
    if size > BODY_LIMIT:
        errors.append(f"{skill_md}: body {size} bytes 超過 {BODY_LIMIT}")
    return errors


def check_links(md: pathlib.Path) -> list[str]:
    errors = []
    for target in LINK.findall(md.read_text(encoding="utf-8")):
        if re.match(r"[a-z]+:", target) or target.startswith("#"):
            continue
        if not (md.parent / target.split("#", 1)[0]).exists():
            errors.append(f"{md}: 連結目標不存在 {target}")
    return errors


def main() -> int:
    errors = []
    for skill_md in sorted(ROOT.glob("skills/*/SKILL.md")):
        errors += check_skill(skill_md)
    for md in sorted(ROOT.glob("**/*.md")):
        if ".git" not in md.parts:
            errors += check_links(md)
    for error in errors:
        print(error, file=sys.stderr)
    print("OK" if not errors else f"{len(errors)} 個問題")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
