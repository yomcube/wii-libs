#!/usr/bin/env python3
import csv
from configparser import ConfigParser, UNNAMED_SECTION
from pathlib import Path, PurePath
from jinja2 import Environment, FileSystemLoader
from yaml import safe_load

LIBS_DIR = Path("libs")
LIBS_YML = LIBS_DIR / "libs.yml"
SOURCES_DIR = Path("sources")
SOURCES_YML = SOURCES_DIR / "sources.yml"

class Source:
    abbr: str
    gameName: str
    shortName: str | None
    gameID: str
    file: str
    link: str | None

class FilePath:
    path: str
    sources: list[Source]
    notes: str | None
    isDir: bool
    purepath: PurePath
    def __init__(self, path: str, sources: list[Source], notes: str | None):
        self.path = path
        self.sources = sources
        self.notes = notes
        self.isDir = path[-1] == "/"
        self.purepath = PurePath(path)
    def __repr__(self):
        return f'{{"path": "{self.path}", "sources": {self.sources}, "notes": "{self.notes}"}}'

class NodePath:
    name: str
    isDir: bool
    sources: list[Source]
    notes: str
    purepath: PurePath
    filepath: FilePath
    children: dict[str, "NodePath"] = {}
    def __init__(self, name: str, isDir: bool, sources: list[Source], notes: str | None, purepath: PurePath, filepath: FilePath):
        self.name = name
        self.isDir = isDir
        self.sources = sources
        self.notes = notes
        self.purepath = purepath
        self.filepath = filepath
        self.children = {}
    def __repr__(self):
        return f'{{"name": {self.name}, "isDir": {self.isDir}, "children": {self.children}}}'

class Line:
    path: str
    sources: str
    notes: str
    def __init__(self, path, sources, notes):
        self.path = path
        self.sources = sources
        self.notes = notes

class Lib:
    name: str
    file: str
    abbr: str
    paths: list[FilePath] = []
    rootNode: NodePath
    lines: list[Line]
    def __init__(self, obj):
        self.name = obj["name"]
        self.file = obj["file"]
        self.abbr = self.file.removesuffix(".csv")
        self.paths = []
        self.rootNode = None
        self.lines = None
    def __repr__(self):
        return f'{{"name": "{self.name}", "file": "{self.file}", "rootNode": {self.rootNode}}}'


wiiTDB = ConfigParser(allow_unnamed_section=True, delimiters=('='))
wiiuTDB = ConfigParser(allow_unnamed_section=True, delimiters=('='))
def initTDBs():
    wiiTDB.read("wiitdb.txt", encoding="utf-8")
    wiiuTDB.read("wiiutdb.txt", encoding="utf-8")

def game_id_link(id: str) -> str | None:
    if wiiTDB.has_option(UNNAMED_SECTION, id):
        return f"https://wiki.dolphin-emu.org/index.php?title={id}"
    if wiiuTDB.has_option(UNNAMED_SECTION, id):
        return f"https://www.gametdb.com/WiiU/{id}"
    return None

def load_sources():
    with SOURCES_YML.open('r') as f:
        sources_obj: list[Source] = safe_load(f)
    sources_obj.sort(key=lambda s: s["gameName"])

    initTDBs()
    for src in sources_obj:
        src["link"] = game_id_link(src["gameID"])
        if not "shortName" in src:
            src["shortName"] = src["gameName"]
    return sources_obj


def paths_to_nodes(paths: list[FilePath]) -> NodePath:
    root = NodePath("", True, [], None, PurePath(), None)

    for p in paths:
        node = root
        parts = p.purepath.parts

        for i, part in enumerate(parts):
            end = i == len(parts) - 1
            if part not in node.children:
                node.children[part] = NodePath(
                    name=part,
                    isDir=(not end) or p.isDir,
                    sources=p.sources,
                    notes=p.notes,
                    purepath=PurePath(*parts[: i+1]),
                    filepath=p
                )
            node = node.children[part]
        node.isDir = p.isDir
    return root

def node_to_lines(node: NodePath, prefix: str = "") -> list[Line]:
    lines: list[Line] = []

    children = sorted(
        node.children.values(),
        key=lambda n: (not n.isDir, n.name.lower()),
    )

    for i, child in enumerate(children):
        last = i == len(children) - 1

        connector = "└── " if last else "├── "
        suffix = "/" if child.isDir else ""

        lines.append(Line(
            f'<span class="prefix" title="{child.filepath.path}">{prefix}{connector}</span>{child.name}{suffix}',
            ", ".join([s["shortName"] for s in child.sources]), child.notes
        ))

        extension = "    " if last else "│   "
        lines.extend(node_to_lines(child, prefix + extension))

    return lines

def load_libs(sources):
    libs = []
    with LIBS_YML.open('r') as f:
        libs_obj: list[Lib] = safe_load(f)
    for lib in libs_obj:
        l = Lib(lib)
        with open(LIBS_DIR / l.file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                src_abbrs = row[1].strip().split("; ")
                srcs = []
                for abbr in src_abbrs:
                    s = next((s for s in sources if s["abbr"] == abbr), None)
                    if s: srcs.append(s)

                p = FilePath(row[0], srcs, row[2] if len(row) > 2 else None)
                l.paths.append(p)
        
        l.rootNode = paths_to_nodes(l.paths)
        l.lines = node_to_lines(l.rootNode)
        libs.append(l)
    return libs


def main():
    sources = load_sources()
    libs = load_libs(sources)

    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)
    template = env.get_template("main.html")
    render = template.render(srcs=sources, libs=libs)
    with open("out.html", 'w', encoding="utf-8") as f:
        f.write(render)

if __name__ == "__main__":
    main()