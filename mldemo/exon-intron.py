import argparse
import random
import korflab

parser = argparse.ArgumentParser()
parser.add_argument('fasta', help='exons file')
parser.add_argument('seqs', type=int, default=20000,
	help='number of sequences')
parser.add_argument('--length', type=int, default=50,
	help='length of exons [%(default)i]')
parser.add_argument('--introns', action='store_true',
	help='remove splice sites from ends of sequences')
arg = parser.parse_args()

seqs = []

for defline, seq in korflab.readfasta(arg.fasta):
	if arg.introns: seqs.append(seq[10:-10])
	else:           seqs.append(seq)

seq = ''.join(seqs)
cds = []
for _ in range(arg.seqs):
	pos = random.randint(0, len(seq) - arg.length)
	cds.append(seq[pos:pos+arg.length])

random.shuffle(cds)

for i in range(arg.seqs):
	if i == arg.seqs: break
	print(cds[i])

