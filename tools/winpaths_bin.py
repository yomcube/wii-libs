import re, sys

regex = re.compile(rb'[A-Za-z]:(?:\\\\|\\|/)[^\x00\r\n\t<>:"|?*]{1,260}')
bites = open(sys.argv[1], 'rb').read()

paths = [
    re.split(r'[\x00\r\n\t]',
        maatch.group().decode('ascii', 'ignore')
    )[0]
    for maatch in regex.finditer(bites)
]

paths = list(set(paths))
paths.sort()

with open("out.txt", 'w') as f:
    f.write('\n'.join(paths))
