import os

dirs = [
    'src/data', 'src/features', 'src/models', 'src/geo', 'src/services',
    'src/ui', 'src/pages', 'src/utils', 'scripts', 'tests', 'docs',
    'output/models', 'data/geo_cache', 'logs'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    if d.startswith('src') or d in ['tests']:
        init_file = os.path.join(d, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('"""Package initialization."""\n')

# Also ensure src/__init__.py exists
src_init = os.path.join('src', '__init__.py')
if not os.path.exists(src_init):
    with open(src_init, 'w', encoding='utf-8') as f:
        f.write('"""UrbanPulse core package."""\n')

print("All directories and packages initialized.")
