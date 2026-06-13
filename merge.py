import sys
import string
import re
import os
import platform
import json


def get_path():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


filter = None
suffixes = set()
if len(sys.argv) >= 2:
    filter = sys.argv[1]
    try:
        with open('rules.json', 'r') as f:
            rules_data = json.load(f)
        
        if filter == 'global_reference':
            for section in rules_data.get('sections', []):
                for rule in section.get('rules', []):
                    for suf in rule.get('suffixes', []):
                        suffixes.add(str(suf))
        else:
            found = False
            for section in rules_data.get('sections', []):
                for rule in section.get('rules', []):
                    if rule.get('id') == filter:
                        for suf in rule.get('suffixes', []):
                            suffixes.add(str(suf))
                        found = True
                        break
                if found:
                    break
            if not found:
                print('Rule ID %s not found in rules.json!' % filter)
                sys.exit(1)
    except Exception as e:
        print('Error reading rules.json:', e)
        sys.exit(1)

nickmap = {}
fnick = open('nickname.txt', 'r')
while True:
    reads = fnick.readline()
    if not reads:
        break
    reads = reads.strip()
    if len(reads) == 0:
        break
    rec = re.split('\s+', reads)
    if len(rec) == 3:
        nickmap[rec[0].upper()] = (rec[1], rec[2])
    else:
        nickmap[rec[0].upper()] = (rec[1], None)
fnick.close()

blacklist = {}
fblacklist = open('blacklist.txt', 'r')
while True:
    reads = fblacklist.readline()
    if not reads:
        break
    reads = reads.strip()
    if len(reads) == 0:
        break
    rec = re.split('\s+', reads)
    blacklist[rec[0] + '\x01' + rec[1]] = 1
fblacklist.close()

path = get_path()
if platform.system() == 'Windows':
    path = path + '\\' + 'records' + '\\'
else:
    path = path + '/' + 'records' + '/'

scoremap = {}
allengines = {}

engine_year_map = {}

def resolve_name(name, file_base):
    name = name.upper()
    if (name + '\x01' + file_base) in blacklist:
        return 'BLACKLIST'
    elif (name + file_base.split('_')[0]) in nickmap:
        mapped = nickmap[name + file_base.split('_')[0]]
        if mapped[1]:
            return mapped[0] + ' ' + mapped[1]
        else:
            return mapped[0]
    elif name in nickmap:
        mapped = nickmap[name]
        if mapped[1]:
            return mapped[0] + ' ' + mapped[1]
        else:
            return mapped[0]
    else:
        match = re.match(r'^([A-Z_\\\-\.]+)([0-9]+)$', name)
        if match:
            n = match.group(1)
            v = match.group(2)
            if len(v) == 2 and (v[0] == '0' or v[0] == '1' or v[0] == '2'):
                v = '20' + v
            if len(v) > 0:
                return n + ' ' + v
        else:
            match = re.match(r'([A-Z_\\-]+)([0-9]*)', name)
            if match:
                n = match.group(1)
                v = match.group(2)
                if len(v) == 2 and (v[0] == '0' or v[0] == '1' or v[0] == '2'):
                    v = '20' + v
                if len(v) > 0:
                    return n + ' ' + v
        return name


for root, dirs, files in os.walk(path):
    for file in files:
        if not file.endswith('.txt'):
            continue
        if filter:
            file_suffix = file.split('.')[0].split('_')[1]
            if file_suffix not in suffixes:
                continue
        curscoremap = {}
        maxscore = 0
        file_base = file.split('.')[0]
        fin = open(path + file, 'r')
        for line in fin:
            line = line.strip()
            if not line:
                continue
            match = re.match(r'^\s*(.+?)\s+-\s+(.+?)\s*:\s*(\d+)\s*:\s*(\d+)\s*$', line)
            if not match:
                continue
            name_a = match.group(1)
            name_b = match.group(2)
            score_a = int(match.group(3))
            score_b = int(match.group(4))
            
            name_a = resolve_name(name_a, file_base)
            name_b = resolve_name(name_b, file_base)
            
            if name_a == 'BLACKLIST' or name_b == 'BLACKLIST':
                continue
                
            allengines[name_a] = 1
            allengines[name_b] = 1
            
            year = int(file[:4])
            engine_year_map.setdefault(name_a, set())
            engine_year_map[name_a].add(year)
            engine_year_map.setdefault(name_b, set())
            engine_year_map[name_b].add(year)
            
            if name_a < name_b:
                engines = (name_a, name_b)
                scores = (score_a, score_b)
            else:
                engines = (name_b, name_a)
                scores = (score_b, score_a)
                
            if engines not in curscoremap:
                curscoremap[engines] = [0, 0]
            curscoremap[engines] = [
                curscoremap[engines][0] + scores[0],
                curscoremap[engines][1] + scores[1]
            ]
            if scores[0] + scores[1] > maxscore:
                maxscore = scores[0] + scores[1]
                
        for engines, scores in curscoremap.items():
            if engines not in scoremap:
                scoremap[engines] = [0, 0, 0]
            if scores[0] + scores[1] > 0:
                scoremap[engines] = [
                    scoremap[engines][0] + scores[0],
                    scoremap[engines][1] + maxscore - scores[0] - scores[1],
                    scoremap[engines][2] + scores[1]
                ]
            else:
                scoremap[engines] = [
                    scoremap[engines][0], scoremap[engines][1],
                    scoremap[engines][2]
                ]
        fin.close()

fname = open('engines.txt', 'w')
allengines = sorted(allengines.keys())
for each in allengines:
    fname.write(each + '\n')
fname.close()

fout = open('score.txt', 'w')
scoremap = sorted(scoremap.items())
for each in scoremap:
    engines = each[0]
    scores = each[1]
    if engines[0].split(' ')[0] != engines[1].split(' ')[0] and engines[
            0] != 'BLACKLIST' and engines[1] != 'BLACKLIST':
        fout.write('\"' + engines[0] + '\"' + '\t' + str(scores[0]) + '\t' +
                   str(scores[1]) + '\t' + str(scores[2]) + '\t' + '\"' +
                   engines[1] + '\"' + '\n')
fout.close()

sorted_engine_year_map = sorted(engine_year_map.items(),
                                key=lambda x: x[0])
if not filter:
    fname = 'engine_year_map'
else:
    fname = 'engine_year_map_' + filter

fout = open(fname + '.txt', 'w')
for engine, years in sorted_engine_year_map:
    fout.write(engine + '\t' + ','.join(map(str, sorted(years))) + '\n')
fout.close()
