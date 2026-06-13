import sys
import re
import string

mingames = 0
out_nn = True
filter = sys.argv[1]
if len(sys.argv) >= 3:
    mingames = int(sys.argv[2])
    if len(sys.argv) >= 4:
        if int(sys.argv[3]) == 0:
            out_nn = False
    
display_name = {}    
try:
    fdisplay = open('displayname.txt','r')
    reads = fdisplay.read()
    reads = reads.split('\n')
    for each in reads:
        ent = each.split('\t')
        if len(ent) == 2:
            display_name[ent[0]] = ent[1]
    fdisplay.close()
except:
    display_name = {}
    
author_list = {}
try:
    fauthor = open('author.txt','r')
    reads = fauthor.read()
    reads = reads.split('\n')
    for each in reads:
        ent = each.split('\t')
        if len(ent) == 3:
            author_list[ent[0]] = (ent[1], ent[2])
    fauthor.close()
except:
    author_list = {}
    
max_year = 0
engine_year_map = {}
active_engines = set()
all_engines = set()
active_names = set()
try:
    fengine = open('engine_year_map_' + filter + '.txt', 'r')
    for line in fengine:
        engine, years = line.strip().split('\t')
        years = list(map(int, years.split(',')))
        engine_year_map[engine] = years
        max_year = max(max_year, max(years))
    fengine.close()
except:
    engine_year_map = {}
for engine, years in engine_year_map.items():
    name = engine.split(' ')[0]
    for year in years:
        all_engines.add(engine)
        if year >= max_year - 4:
            print((year, engine))
            active_engines.add(engine)
            active_names.add(name)
for engine in all_engines:
    name = engine.split(' ')[0]
    if not name in active_names:
        active_engines.add(engine) 

fout = open('active_engines_' + filter + '.txt', 'w')
for engine in sorted(active_engines):
    fout.write(engine + '\n')
fout.close()        
            
benchmark = {}
try:
    fbench = open('benchmark.txt', 'r')
    while True:
        reads = fbench.readline()
        if not reads:
            break
        reads = reads.strip()
        if len(reads) == 0:
            break
        bc = re.split('\t', reads)
        benchmark[bc[0]] = (int(bc[1]), len(benchmark))
    fbench.close()
except:
    benchmark = {}
bias = 0
biaspriority = 10000

engines = {}
all_ratings = []
key_ratings = []
output = []
fin = open('ratings.txt', 'r')
append_name = ''
if mingames > 0:
    append_name = '_' + '_'.join(sys.argv[1:])
fout = open('ratings_merge' + append_name + '.html', 'w')
title = fin.readline().rstrip('\n')
posN = 0
posE = 0
posG = 0
posO = 0
for i in range(len(title)):
    if title[i] == 'N':
        posN = i
    if title[i] == 'E':
        posE = i - 1
    if title[i] == 'g':
        posG = i - 1
    if title[i] == '.':
        posO = i - 3
        break
while True:
    reads = fin.readline()
    if not reads:
        break
    reads = reads.rstrip('\n')
    reads1 = reads[posN:posE]
    reads2 = reads[posE:posE+4]
    reads3 = reads[posE+4:]
    games = int(reads[posG:posG+6].strip())
    reads = reads[posN:]
    name = reads.split(' ')[0]
    rating = int(reads2.strip())
    all_ratings.append(rating)
    if name not in engines and games >= mingames and reads1.strip() in active_engines:
        engines[name] = 1
        rank = str(len(engines))
        key_ratings.append(rating)
        output.append(' ' * (posN - 1 - len(rank)) + rank + ' ' + reads)
    else:
        if out_nn:
            output.append(' ' * posN + reads)
    if len(benchmark) > 0 and reads1.strip() in benchmark:
        cur = benchmark[reads1.strip()]
        if cur[1] < biaspriority:
            bias = cur[0] - rating
            biaspriority = cur[1]
        
if len(benchmark) == 0:
    bias = 1600 - int(round(sum(key_ratings) / len(key_ratings)))
fout.write('<TABLE border=1>\n')
fout.write('<TBODY>\n')
fout.write('<TR><TH>Rank</TH><TH>Name</TH><TH>Elo</TH><TH>+</TH><TH>-</TH><TH>games</TH><TH>score</TH><TH>oppo.</TH><TH>draws</TH><TH>Author</TH><TH>Place</TH></TR>\n')
for each in output:
    fout.write('<TR>')
    fout.write('<TD>')
    fout.write(each[:posN].strip())
    fout.write('</TD>')
    fout.write('<TD>')
    name = each[posN:posE].strip()
    raw_name = name.split(' ')[0]
    orig_name = name
    if name in display_name:
        name = display_name[name]
    fout.write(name)
    fout.write('</TD>')
    rating = int(each[posE:posE+4].strip()) + bias
    fout.write('<TD>')
    fout.write(str(rating))
    fout.write('</TD>')
    oind = -4
    for ent in re.split('\s+', each[posE+4:].strip()):
        fout.write('<TD>')
        if oind != 0:
            fout.write(ent)
        else:
            oppo = int(ent) + bias
            fout.write(str(oppo))
        fout.write('</TD>')
        oind += 1
    if orig_name in author_list:
        author, place = author_list[orig_name]
    elif raw_name in author_list:
        author, place = author_list[raw_name]
    else:
        author, place = '', ''
    fout.write('<TD>')
    fout.write(str(author))
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write('<IMG src="/static/flags/' + str(place) + '.svg" style="width:1.6em;vertical-align:middle;" alt="flag"/> <span style="font-family:Consolas,monaco,monospace;">' + str(place) + '</span>')
    fout.write('</TD>')
    fout.write('</TR>\n')
fout.write('</TBODY>\n')
fout.write('</TABLE>\n')
fin.close()
fout.close()