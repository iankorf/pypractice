import argparse
import sys
import korflab

parser = argparse.ArgumentParser(description='count kmers')
parser.add_argument('fasta', help='input fasta file')
parser.add_argument('k', type=int, help='size of k')
parser.add_argument('--prob', action='store_true',
	help='report probabilities instead of counts')
arg = parser.parse_args()

if arg.k > 10: sys.exit(f'{sys.argv[0]} not designed for large values of k')
kdict = korflab.kmers(arg.k, init=1)

for name, seq in korflab.readfasta(arg.fasta):
	for i in range(len(seq) - arg.k + 1):
		kmer = seq[i:i+arg.k]
		if kmer in kdict: kdict[kmer] += 1

if arg.prob:
	total = sum(kdict.values())
	for k, v in kdict.items(): kdict[k] = v / total

for kmer, value in kdict.items():
	print(kmer, value, sep='\t')
