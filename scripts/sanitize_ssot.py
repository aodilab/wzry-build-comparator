import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from config.hero_official_builds import OFFICIAL_HERO_BUILDS
from config.hero_arcana_data import HERO_RECOMMENDED_ARCANA

cleaned = {}
for name, data in OFFICIAL_HERO_BUILDS.items():
    lanes = data.get('lanes', {})
    valid_lanes = {}
    default_arc = HERO_RECOMMENDED_ARCANA.get(name, {'red': '异变', 'green': '鹰眼', 'blue': '隐匿'})
    default_arc_map = {
        'red': {default_arc.get('red', '异变'): 10},
        'green': {default_arc.get('green', '鹰眼'): 10},
        'blue': {default_arc.get('blue', '隐匿'): 10}
    }
    r = default_arc.get('red', '异变')
    b_arc = default_arc.get('blue', '隐匿')
    g = default_arc.get('green', '鹰眼')
    default_arc_desc = f'10{r} 10{b_arc} 10{g}'

    for lane_name, builds in lanes.items():
        if len(builds) > 0:
            valid_builds = []
            seen_genres = set()
            for b in builds:
                genre = b.get('genre', '')
                if genre not in seen_genres and len(b.get('items', [])) >= 4:
                    seen_genres.add(genre)
                    if not b.get('arcana') or not any(b.get('arcana').values()):
                        b['arcana'] = default_arc_map
                        b['arcana_desc'] = default_arc_desc
                    valid_builds.append(b)
                if len(valid_builds) >= 3:
                    break
            if valid_builds:
                valid_lanes[lane_name] = valid_builds

    if valid_lanes:
        cleaned[name] = {
            'supported_lanes': list(valid_lanes.keys()),
            'lanes': valid_lanes
        }

print(f'Cleaned {len(cleaned)} heroes with valid builds.')
with open('config/hero_official_builds.py', 'w', encoding='utf-8') as f:
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('"""王者荣耀国服全英雄官方真实推荐出装与铭文全量数据库 SSOT"""\n\n')
    f.write('null = None\nfalse = False\ntrue = True\n\n')
    f.write('OFFICIAL_HERO_BUILDS = ' + json.dumps(cleaned, ensure_ascii=False, indent=2) + '\n')

print('Successfully written cleaned SSOT to config/hero_official_builds.py')
