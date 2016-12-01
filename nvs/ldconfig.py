import os
import re

import sh


def parse_ldconfig_p(data):
    """
    Returns dictionary representation of ldconfig -p output

    NOTE: This is a nasty hack but works for now
    """
    ldcache = []
    r = re.compile('^(.*) \((.*)\) => (.*)$')
    hwcap_prefix = 'hwcap:'
    abi_prefix = 'OS ABI:'
    for line in data:
        m = r.match(line)
        name, meta, path = m.groups()
        realpath = os.path.realpath(path)
        parts = meta.split(', ')
        elf = parts[0]
        hwcap, abi = None, None
        for part in parts:
            if part.startswith(hwcap_prefix):
                hwcap = part.split(hwcap_prefix)[-1].strip()
            elif part.startswith(abi_prefix):
                abi = part.split(abi_prefix)[-1].strip()
        ldcache.append(dict(name=name.strip(), elf=elf, hwcap=hwcap,
                            abi=abi, path=path, realpath=realpath))
    return ldcache


def get_ldconfig_cache():
    """
    Fetch and return dictionary representation of ldconfig -p
    """
    ldconfig = sh.Command('ldconfig')
    libs = ldconfig('-p').stdout.splitlines()[1:]
    return parse_ldconfig_p(libs)


def get_libs(names, ldcache=None):
    """
    Returns map of 32bit and 64bit libs matching names
    """
    ldcache = ldcache or get_ldconfig_cache()
    libs = {
        'lib32': [],
        'lib64': [],
    }
    r = re.compile('^({})'.format('|'.join(names)))
    r_x86 = re.compile('libc[4-6]')
    r_x86_64 = re.compile(r_x86.pattern + ',x86-64')
    for lib in ldcache:
        if not r.search(lib['name']):
            continue
        elf = lib['elf']
        if r_x86_64.search(elf):
            libs['lib64'].append(lib)
        elif r_x86.search(elf):
            libs['lib32'].append(lib)
    return libs


def ldd(lib_path):
    """
    Returns dictionary of ldd on a library path
    """
    ldd = sh.Command('ldd')
    ldd_out = ldd(lib_path)
    libraries = {}
    for line in ldd_out.splitlines():
        match = re.match(r'(.*) => (.*) \(0x', line)
        if match:
            libraries[match.group(1).strip()] = match.group(2)
    return libraries
