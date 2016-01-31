import sys
import re
import string

mingames = 0
out_nn = True
if len(sys.argv) >= 2:
	mingames = string.atoi(sys.argv[1])
	if len(sys.argv) >= 3:
		if string.atoi(sys.argv[2]) == 0:
			out_nn = False
benchmark = None
try:
	fbench = open('benchmark.txt', 'r')
	benchmark = re.split('\s+', fbench.readline().strip())
	benchmark = (benchmark[0], string.atoi(benchmark[1]))
	fbench.close()
except:
	benchmark = None

engines = {}
all_ratings = []
key_ratings = []
output = []
fin = open('ratings.txt', 'r')
append_name = ''
if mingames > 0:
	append_name = '_' + str(mingames)
fout = open('ratings_merge' + append_name + '.txt', 'w')
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
fout.write(title + '\n')
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
	if benchmark and benchmark[0] == reads1.strip():
		bias = 1600 - rating
		
if not benchmark:
	bias = 1600 - int(round(sum(key_ratings) / len(key_ratings)))
for each in output:
	rating = string.atoi(each[posE:posE+4].strip()) + bias
	rating = str(rating)
	rating = ' ' * (4 - len(rating)) + rating
	fout.write(each[:posE] + rating + each[posE+4:] + '\n')
fin.close()
fout.close()