import glob
import os

biomes_map = {
    'human.yaml': ['plains', 'forest', 'lake'],
    'halfling.yaml': ['plains', 'forest'],
    'elf.yaml': ['forest'],
    'dwarf.yaml': ['mountain'],
    'orc.yaml': ['wasteland', 'desert', 'mountain', 'plains'],
    'beastman.yaml': ['forest', 'plains'],
    'fairy.yaml': ['forest', 'lake'],
    'half_beast.yaml': ['plains', 'forest', 'wasteland'],
    'angel_demon.yaml': ['mountain', 'desert', 'wasteland'],
    'dragon.yaml': ['mountain'],
    'undead.yaml': ['wasteland', 'desert', 'snow'],
    'elemental.yaml': ['mountain', 'lake', 'desert', 'snow'],
    'golem.yaml': ['mountain', 'wasteland', 'desert']
}

files = glob.glob('configs/races/**/*.yaml', recursive=True)
for f in files:
    filename = os.path.basename(f)
    print(f"Reading {f}")
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'preferred_biomes:' not in content:
        b_list = biomes_map.get(filename, ['plains'])
        b_str = repr(b_list).replace("'", '"')
        content = content.replace('tier: ', 'preferred_biomes: ' + b_str + '\ntier: ')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print('Updated ' + filename)
    else:
        print('Already updated ' + filename)
