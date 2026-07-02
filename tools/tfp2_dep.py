import glob

paths = []

for fname in glob.glob("*.d"):
    with open(fname, 'r') as f:
        lines = f.readlines()
        lines[0] = lines[0].split(": ")[1]
        for line in lines:
            line = line.strip()
            paths.append(line.removesuffix("  \\") if line[-3::1] == '  \\' else line)

paths = list(set(paths))
paths.sort()

with open("__out.txt", 'w') as f:
    for p in paths:
        f.write(f"{p}\n")
