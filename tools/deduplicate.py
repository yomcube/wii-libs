import sys

if len(sys.argv) < 2:
    print("python remove_duplicates.py file [file2] [...]")
    sys.exit(0)

def tr(s: str) -> str:
    return s.translate(str.maketrans({"\\": "\0"})).casefold() # make dir separator come first  

def new(s: str) -> str:
    return s.replace("\\\\", "\\").replace("/", "\\")

for fname in sys.argv[1:]:
    with open(fname, 'r') as f:
        oldlines = f.readlines()
    newlines = [new(l) for l in oldlines]
    with open(fname, 'w') as f:
        f.writelines(sorted(set(newlines), key=tr))
