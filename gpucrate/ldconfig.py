import os
import re

import sh


def parse_ldconfig_p(data, follow_links=False):
    """
    Returns dictionary representation of ldconfig -p

    NOTE: This is a nasty hack but works for now
    """
    ldcache = {} if follow_links else []
    r = re.compile('^(.*) \((.*)\) => (.*)$')
    hwcap_prefix = 'hwcap:'
    abi_prefix = 'OS ABI:'
    for line in data:
        m = r.match(line)
        name, meta, path = m.groups()
        if follow_links:
            path = os.path.realpath(path)
        parts = meta.split(', ')
        elf = parts[0]
        hwcap, abi = None, None
        for part in parts:
            if part.startswith(hwcap_prefix):
                hwcap = part.split(hwcap_prefix)[-1].strip()
            elif part.startswith(abi_prefix):
                abi = part.split(abi_prefix)[-1].strip()
        if follow_links:
            ldcache[path] = dict(name=name.strip(), elf=elf, hwcap=hwcap,
                                 abi=abi, path=path)
        else:
            ldcache.append(dict(name=name.strip(), elf=elf, hwcap=hwcap,
                                abi=abi, path=path))
    if follow_links:
        return ldcache.values()
    else:
        return ldcache


def get_ldconfig_cache(follow_links=False):
    """
    Fetch and return dictionary representation of ldconfig -p
    """
    ldconfig = sh.Command('ldconfig')
    libs = ldconfig('-p').stdout.splitlines()[1:]
    return parse_ldconfig_p(libs, follow_links=follow_links)


def get_libs(names, ldcache=None, follow_links=False):
    """
    Returns map of 32bit and 64bit libs matching names
    """
    ldcache = ldcache or get_ldconfig_cache(follow_links=follow_links)
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
    ldd_out = ldd(lib_path).stdout.splitlines()
    libraries = {}
    for line in ldd_out:
        match = re.match(r'([^\s]+) => ([^\s]+) \(0x', line)
        if match:
            libraries[match.group(1).strip()] = match.group(2)
    return libraries
