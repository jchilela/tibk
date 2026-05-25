#!/usr/bin/env python3
import re

with open('templates/protocolo.html') as f:
    content = f.read()

ifs = len(re.findall(r'\{%-?\s*if\s', content))
endifs = len(re.findall(r'\{%-?\s*endif\s*-?%\}', content))
fors = len(re.findall(r'\{%-?\s*for\s', content))
endfors = len(re.findall(r'\{%-?\s*endfor\s*-?%\}', content))
blocks = len(re.findall(r'\{%-?\s*block\s', content))
endblocks = len(re.findall(r'\{%-?\s*endblock\s*-?%\}', content))

print(f"if/endif: {ifs}/{endifs} ({'OK' if ifs==endifs else 'ERROR'})")
print(f"for/endfor: {fors}/{endfors} ({'OK' if fors==endfors else 'ERROR'})")
print(f"block/endblock: {blocks}/{endblocks} ({'OK' if blocks==endblocks else 'ERROR'})")
