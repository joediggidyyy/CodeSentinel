from pathlib import Path

cli_dir = Path('codesentinel/cli')
files = []

for py_file in cli_dir.glob('*.py'):
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        files.append((py_file.name, line_count))
    except Exception as e:
        print(f"Error reading {py_file.name}: {e}")

files.sort(key=lambda x: x[1], reverse=True)

print(f"{'File':<40} {'Lines':>8}")
print("=" * 50)
for name, lines in files:
    print(f"{name:<40} {lines:>8}")

print("=" * 50)
print(f"{'TOTAL':<40} {sum(l for _, l in files):>8}")
