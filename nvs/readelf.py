import re

import sh

def get_soname(lib):
    readelf = sh.Command('readelf')
    r = re.compile('Library\s+soname:\s+\[(.+)\]')
    out = readelf('-d', lib).stdout
    m = r.search(out)
    if m:
        return m.groups()[0]
