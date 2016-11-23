import re
import sh


def get_ldconfig_cache():
    """
    Returns dictionary of ldconfig -p
    """
    ldconfig = sh.Command('ldconfig')
    libs = ldconfig('-p').stdout.splitlines()[1:]
    ldcache = []
    for lib in libs:
        parts = lib.split()
        name = parts[0]
        path = parts[-1]
        if len(parts) > 4:
            arch = ' '.join(parts[1:-2])
        else:
            arch = parts[1]
        arch = arch.split(',')[-1].strip('(').strip(')')
        ldcache.append(dict(name=name, arch=arch, path=path))
    return ldcache


def get_libs(names):
    """
    Returns map of 32bit and 64bit libs matching names
    """
    ldcache = get_ldconfig_cache()
    archmap = {
        'libc6': 'lib32',
        'x86-64': 'lib64',
    }
    libs = {
        'lib32': [],
        'lib64': [],
    }
    r = re.compile('({})'.format('|'.join(['^{}'.format(i) for i in names])))
    for lib in ldcache:
        arch = lib['arch']
        if not r.search(lib['name']) or arch not in ['libc6', 'x86-64']:
            continue
        libs[archmap[arch]].append(lib)
    return libs
