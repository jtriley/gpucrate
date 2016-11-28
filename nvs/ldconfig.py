import re
import sh


def get_ldconfig_cache():
    """
    Returns dictionary representation of ldconfig -p

    NOTE: This is a nasty hack but works for now
    """
    ldconfig = sh.Command('ldconfig')
    libs = ldconfig('-p').stdout.splitlines()[1:]
    ldcache = []
    r = re.compile('^(.*) \((.*)\) => (.*)$')
    hwcap_prefix = 'hwcap:'
    abi_prefix = 'OS ABI:'
    for lib in libs:
        m = r.match(lib)
        name, meta, path = m.groups()
        parts = meta.split(', ')
        elf = parts[0]
        hwcap, abi = None, None
        for part in parts:
            if part.startswith(hwcap_prefix):
                hwcap = part.split(hwcap_prefix)[-1].strip()
            elif part.startswith(abi_prefix):
                abi = part.split(abi_prefix)[-1].strip()
        ldcache.append(dict(name=name.strip(), elf=elf, hwcap=hwcap,
                            abi=abi, path=path))
    return ldcache


def get_libs(names):
    """
    Returns map of 32bit and 64bit libs matching names
    """
    ldcache = get_ldconfig_cache()
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
