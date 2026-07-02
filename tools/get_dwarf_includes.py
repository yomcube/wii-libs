#!/usr/bin/env python3
# pip install pyelftools

from os.path import join
from sys import argv
from elftools.elf.elffile import ELFFile

def decode(val):
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return str(val)

def main():
    if len(argv) != 2:
        return
    
    with open(argv[1], "rb") as f:
        elf = ELFFile(f)

        if not elf.has_dwarf_info():
            print("No DWARF")
            return

        dwarf = elf.get_dwarf_info()

        fnames = []

        for cu in dwarf.iter_CUs():
            lineprog = dwarf.line_program_for_CU(cu)
            if lineprog is None:
                continue

            header = lineprog.header
            top_die = cu.get_top_DIE()
            attr = top_die.attributes.get("DW_AT_comp_dir")
            if not attr:
                return None
            comp_dir = decode(attr.value)

            include_dirs = [decode(d) for d in header.include_directory]

            for entry in header.file_entry:
                name = decode(entry.name)

                if name == "(command-line defines)":
                    continue

                if entry.dir_index == 0:
                    if comp_dir:
                        full_path = join(comp_dir, name)
                    else:
                        full_path = name
                else:
                    directory = include_dirs[entry.dir_index - 1]
                    full_path = join(directory, name)

                fnames.append(full_path)

        fnames = sorted(set(fnames), key=str.casefold)
        for fname in fnames:
            print(fname)

if __name__ == "__main__":
    main()
