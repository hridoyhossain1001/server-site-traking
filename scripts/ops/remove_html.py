import os

file_path = "app/main.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.startswith('MARKETING_PAGE = r"""'):
        skip = True
        continue
    if skip and line.startswith('"""'):
        skip = False
        continue
    if not skip:
        new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Removed MARKETING_PAGE from main.py")
