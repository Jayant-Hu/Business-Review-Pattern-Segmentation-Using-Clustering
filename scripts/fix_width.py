import glob

for f in glob.glob('src/pages/*.py'):
    with open(f, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    changed = False
    new_lines = []
    for l in lines:
        if 'width=' in l and '100%' in l and '#map' not in l:
            idx = l.find('width=')
            end_quote = l.find('%', idx) + 2
            target = l[idx:end_quote]
            l_new = l.replace(target, 'use_container_width=True')
            new_lines.append(l_new)
            changed = True
        else:
            new_lines.append(l)
    if changed:
        with open(f, 'w', encoding='utf-8') as fp:
            fp.writelines(new_lines)
        print('Updated:', f)
