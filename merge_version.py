import sys
import re
import string

mingames = 0
out_nn = True
if len(sys.argv) >= 3:
	mingames = string.atoi(sys.argv[2])
	if len(sys.argv) >= 4:
		if string.atoi(sys.argv[3]) == 0:
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
		benchmark[bc[0]] = (string.atoi(bc[1]), len(benchmark))
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
for i in range(len(title)):
	if title[i] == 'N':
		posN = i
	if title[i] == 'E':
		posE = i - 1
	if title[i] == 'g':
		posG = i - 1
		break
while True:
	reads = fin.readline()
	if not reads:
		break
	reads = reads.rstrip('\n')
	reads1 = reads[posN:posE]
	reads2 = reads[posE:posE+4]
	reads3 = reads[posE+4:]
	games = string.atoi(reads[posG:posG+6].strip())
	reads = reads[posN:]
	name = reads.split(' ')[0]
	rating = string.atoi(reads2.strip())
	all_ratings.append(rating)
	if not engines.has_key(name) and games >= mingames:
		engines[name] = 1
		rank = str(len(engines))
		key_ratings.append(rating)
		output.append(' ' * (posN - 1 - len(rank)) + rank + ' ' + reads)
	else:
		if out_nn:
			output.append(' ' * posN + reads)
	if len(benchmark) > 0 and benchmark.has_key(reads1.strip()):
		cur = benchmark[reads1.strip()]
		if cur[1] < biaspriority:
			bias = cur[0] - rating
			biaspriority = cur[1]
		
if len(benchmark) == 0:
	bias = 1600 - int(round(sum(key_ratings) / len(key_ratings)))
fout.write('<TABLE border=1>\n')
fout.write('<TBODY align=center>\n')
fout.write('<TR><TH>Rank</TH><TH>Name</TH><TH>Elo</TH><TH>+</TH><TH>-</TH><TH>games</TH><TH>score</TH><TH>oppo.</TH><TH>draws</TH></TR>\n')
for each in output:
	fout.write('<TR>')
	fout.write('<TH>')
	fout.write(each[:posN].strip())
	fout.write('</TH>')
	fout.write('<TD>')
	name = each[posN:posE].strip()
	if display_name.has_key(name):
		name = display_name[name]
	fout.write(name)
	fout.write('</TD>')
	rating = string.atoi(each[posE:posE+4].strip()) + bias
	fout.write('<TD>')
	fout.write(str(rating))
	fout.write('</TD>')
	for ent in re.split('\s+', each[posE+4:].strip()):
		fout.write('<TD>')
		fout.write(ent)
		fout.write('</TD>')
	fout.write('</TR>\n')
fout.write('</TBODY>\n')
fout.write('</TABLE>\n')
fin.close()
fout.close()