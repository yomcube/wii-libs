#!/usr/bin/env python3
# Searches for Windows paths in text files
# Useful in linker maps or DWARF dumps
import re
import sys
from os import environ

regex = r'.:[\\/].*'
out = environ.get("R_DOT_PY__OUT", "out.txt") 
mode = environ.get("R_DOT_PY__MODE", 'w')

if len(sys.argv) < 2:
    sys.exit()

text = ""
with open(sys.argv[1], 'r') as f:
    print("reading file...")
    text = f.read()

print("finding strings...")
strs = re.findall(regex, text, flags=re.A)

# Remove duplicates by ensuring that C:\\path\\to\\file == C:\path\to\file == C:/path/to/file
print("\\\\ -> \\ -> /")
for idx, val in enumerate(strs):
    strs[idx] = val.replace("\\\\", '\\').replace('\\', '/').replace("//", '/').replace('")', '').replace('"', '').strip()

print("removing duplicates...")
strs = list(set(strs))

print("sorting strings...")
strs.sort(key=str.lower)

print("writing strings...")
with open(out, mode) as f:
    for s in strs:
        f.write(f"{s}\n")
