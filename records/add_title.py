import sys
import string

f = sys.argv[1]
titles = ['-']
lines = []
fin = open(f, 'r')
for line in fin:
    t = line.strip().split('\t')[0]
    titles.append(t)
    lines.append(line.strip())
fin.close()

fout = open(f, 'w')
fout.write('\t'.join(titles) + '\n')
for line in lines:
    fout.write(line + '\n')
fout.close()
