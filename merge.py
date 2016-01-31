import sys
import string
import re
import os
import platform

def get_path():
     path = sys.path[0]
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)

filter = None
if len(sys.argv) >= 2:
	filter = sys.argv[1]
		 
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
		nickmap[str.upper(rec[0])] = (rec[1], rec[2])
	else:
		nickmap[str.upper(rec[0])] = (rec[1], None)
fnick.close()

path = get_path()
if platform.system() == 'Windows':
	path = path + '\\' + 'records' + '\\'
else:
	path = path + '/' + 'records' + '/'

scoremap = {}
allengines = {}

for root, dirs, files in os.walk(path):
	for file in files:
		if filter:
			if not file.split('.')[0].split('_')[1] in filter:
				continue
		curscoremap = {}
		maxscore = 0
		fin = open(path + file, 'r')
		reads = fin.readline().strip()
		reads = str.upper(reads)
		names = re.split('\s+', reads)[1:]
		for i in range(len(names)):
			if nickmap.has_key(names[i] + file.split('_')[0]):
				names[i] = nickmap[names[i] + file.split('_')[0]]
				if names[i][1]:
					names[i] = names[i][0] + ' ' + names[i][1]
				else:
					names[i] = names[i][0]
			elif nickmap.has_key(names[i]):
				names[i] = nickmap[names[i]]
				if names[i][1]:
					names[i] = names[i][0] + ' ' + names[i][1]
				else:
					names[i] = names[i][0]
			else:
				match = re.match(r'([A-Z_\\-]+)([0-9]*)', names[i])
				if match:
					name = match.group(1)
					version = match.group(2)
					if len(version) == 2 and (version[0] == '0' or version[0] == '1'):
						version = '20' + version
					if len(version) > 0:
						names[i] = name + ' ' + version
			allengines[names[i]] = 1
		for i in range(len(names)):
			reads = fin.readline().strip()
			points = re.split('\s+', reads)[1:]
			j = 0
			winscore = None
			losscore = None
			for each in points:
				if each == '-':
					j += 1
				elif each == ':':
					pass
				elif losscore == None:
					losscore = string.atoi(each)
				else:
					winscore = string.atoi(each)
					if string.atof(file[:4]) <= 2005:
						winscore, losscore = losscore, winscore
					engines = (names[i], names[j])
					if names[i] < names[j]:
						engines = (names[i], names[j])
						scores = (winscore, losscore)
						if not curscoremap.has_key(engines):
							curscoremap[engines] = [0, 0]
						curscoremap[engines] = [curscoremap[engines][0] + scores[0], curscoremap[engines][1] + scores[1]]
						if scores[0] + scores[1] > maxscore:
							maxscore = scores[0] + scores[1]
					j += 1
					winscore = None
					losscore = None
		for engines, scores in curscoremap.iteritems():
			if not scoremap.has_key(engines):
				scoremap[engines] = [0, 0, 0]
			scoremap[engines] = [scoremap[engines][0] + scores[0], scoremap[engines][1] + maxscore - scores[0] - scores[1], scoremap[engines][2] + scores[1]]
		fin.close()
		
fname = open('engines.txt', 'w')
allengines = sorted(allengines.keys())
for each in allengines:
	fname.write(each + '\n')
fname.close()

fout = open('score.txt', 'w')
scoremap = sorted(scoremap.iteritems())
for each in scoremap:
	engines = each[0]
	scores = each[1]
	if engines[0].split(' ')[0] != engines[1].split(' ')[0] and engines[0] != 'BLACKLIST' and engines[1] != 'BLACKLIST':
		fout.write('\"' + engines[0] + '\"' + '\t' + str(scores[0]) + '\t' + str(scores[1]) + '\t' + str(scores[2]) + '\t' + '\"' + engines[1] + '\"' + '\n')
fout.close()

