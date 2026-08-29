import os, sys

exclude_dirs = {"tests", "node_modules", ".git", "coverage", "dist", "build", ".system_generated", ".pytest_cache", "__pycache__", "scratch", "scripts"}
valid_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml", ".sql", ".tf", ".md"}

total_lines = 0
file_count = 0
lang_lines = {}

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.endswith("__pycache__")]
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_extensions and not f.endswith(".pyc") and not f.endswith(".zip"):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                    lines = fp.readlines()
                    cnt = len([l for l in lines if l.strip()])
                    total_lines += cnt
                    file_count += 1
                    lang_lines[ext] = lang_lines.get(ext, 0) + cnt
            except Exception:
                pass

print(f"Total Production LOC: {total_lines} across {file_count} source files")
for ext, cnt in sorted(lang_lines.items(), key=lambda x: x[1], reverse=True):
    print(f"  {ext}: {cnt} lines")

if total_lines >= 50000:
    print("STATUS: PASS (Requirement >= 50,000 LOC satisfied)")
    sys.exit(0)
else:
    print("STATUS: FAIL")
    sys.exit(1)
