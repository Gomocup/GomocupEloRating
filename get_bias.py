import sys
import re
import string
import re

base_bias = 0

if len(sys.argv) == 4:
    pass
elif len(sys.argv) == 5:
    base_bias = string.atoi(sys.argv[4])
else:
    print 'Parameter error!'
    sys.exit(1)

compmap = {}    
fin = open(sys.argv[3], 'r')
read_head = False
while True:
    reads = fin.readline()
    if reads.startswith('<TABLE') or reads.startswith('<TBODY'):
        continue
    elif reads.startswith('</TBODY'):
        break
    elif reads.startswith('<TR'):
        if not read_head:
            read_head = True
        else:
            match = re.match('<TR><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)%</TD><TD>(.*)</TD><TD>(.*)%</TD><TD>(.*)</TD><TD>(.*)</TD></TR>', reads)
            name = match.group(2)
            intelo = string.atoi(match.group(3))
            compmap[name] = intelo
fin.close()

sum_rating = 0
count_rating = 0
records = []
fin = open(sys.argv[1], 'r')
read_head = False
while True:
    reads = fin.readline()
    if reads.startswith('<TABLE') or reads.startswith('<TBODY'):
        continue
    elif reads.startswith('</TBODY'):
        break
    elif reads.startswith('<TR'):
        if not read_head:
            read_head = True
        else:
            match = re.match('<TR><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)%</TD><TD>(.*)</TD><TD>(.*)%</TD><TD>(.*)</TD><TD>(.*)</TD></TR>', reads)
            rank = match.group(1)
            name = match.group(2)
            elo = match.group(3)
            intelo = string.atoi(elo)
            plus = match.group(4)
            minus = match.group(5)
            games = match.group(6)
            score = match.group(7)
            oppo = match.group(8)
            draws = match.group(9)
            author = match.group(10)
            place = match.group(11)
            if compmap.has_key(name):
                bias = compmap[name] - intelo
                sum_rating += bias
                count_rating += 1
            records.append((rank, name, elo, plus, minus, games, score, oppo, draws, author, place))
fin.close()

records_0 = []
fin = open(sys.argv[2], 'r')
read_head = False
while True:
    reads = fin.readline()
    if reads.startswith('<TABLE') or reads.startswith('<TBODY'):
        continue
    elif reads.startswith('</TBODY'):
        break
    elif reads.startswith('<TR'):
        if not read_head:
            read_head = True
        else:
            match = re.match('<TR><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)</TD><TD>(.*)%</TD><TD>(.*)</TD><TD>(.*)%</TD><TD>(.*)</TD><TD>(.*)</TD></TR>', reads)
            rank = match.group(1)
            name = match.group(2)
            elo = match.group(3)
            plus = match.group(4)
            minus = match.group(5)
            games = match.group(6)
            score = match.group(7)
            oppo = match.group(8)
            draws = match.group(9)
            author = match.group(10)
            place = match.group(11)
            records_0.append((rank, name, elo, plus, minus, games, score, oppo, draws, author, place))
fin.close()

bias = int(round(sum_rating * 1.0 / count_rating)) + base_bias

fout = open(sys.argv[1], 'w')
fout.write('<TABLE border=1>\n')
fout.write('<TBODY>\n')
fout.write('<TR><TH>Rank</TH><TH>Name</TH><TH>Elo</TH><TH>+</TH><TH>-</TH><TH>games</TH><TH>score</TH><TH>oppo.</TH><TH>draws</TH><TH>Author</TH><TH>Place</TH></TR>\n')
for each in records:
    fout.write('<TR>')
    fout.write('<TD>')
    fout.write(each[0])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[1])
    fout.write('</TD>')
    rating = string.atoi(each[2]) + bias
    fout.write('<TD>')
    fout.write(str(rating))
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[3])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[4])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[5])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[6])
    fout.write('%</TD>')
    oppo = string.atoi(each[7]) + bias
    fout.write('<TD>')
    fout.write(str(oppo))
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[8])
    fout.write('%</TD>')
    fout.write('<TD>')
    fout.write(each[9])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[10])
    fout.write('</TD>')
    fout.write('</TR>\n')
fout.write('</TBODY>\n')
fout.write('</TABLE>\n')
fout.close()

fout = open(sys.argv[2], 'w')
fout.write('<TABLE border=1>\n')
fout.write('<TBODY>\n')
fout.write('<TR><TH>Rank</TH><TH>Name</TH><TH>Elo</TH><TH>+</TH><TH>-</TH><TH>games</TH><TH>score</TH><TH>oppo.</TH><TH>draws</TH><TH>Author</TH><TH>Place</TH></TR>\n')
for each in records_0:
    fout.write('<TR>')
    fout.write('<TD>')
    fout.write(each[0])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[1])
    fout.write('</TD>')
    rating = string.atoi(each[2]) + bias
    fout.write('<TD>')
    fout.write(str(rating))
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[3])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[4])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[5])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[6])
    fout.write('%</TD>')
    oppo = string.atoi(each[7]) + bias
    fout.write('<TD>')
    fout.write(str(oppo))
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[8])
    fout.write('%</TD>')
    fout.write('<TD>')
    fout.write(each[9])
    fout.write('</TD>')
    fout.write('<TD>')
    fout.write(each[10])
    fout.write('</TD>')
    fout.write('</TR>\n')
fout.write('</TBODY>\n')
fout.write('</TABLE>\n')
fout.close()