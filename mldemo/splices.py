import argparse
import random
import korflab

parser = argparse.ArgumentParser()
parser.add_argument('fasta', help='intron file')
parser.add_argument('--acc', default='acc.txt',
	help='output acceptor file [%(default)s]')
parser.add_argument('--don', default='don.txt',
	help='output donor file [%(default)s]')
parser.add_argument('--length', type=int, default=10,
	help='length of site [%(default)i]')
arg = parser.parse_args()

acc = []
don = []
for defline, seq in korflab.readfasta(arg.fasta):
	d = seq[:arg.length]
	a = seq[-arg.length:]
	if d.startswith('GT'): don.append(d)
	if a.endswith('AG'): acc.append(a)

random.shuffle(acc)
random.shuffle(don)

with open(arg.acc, 'w') as afp:
	for a in acc: print(a, file=afp)

with open(arg.don, 'w') as dfp:
	for d in don: print(d, file=dfp)
