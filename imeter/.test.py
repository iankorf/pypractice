import argparse
import math
import sys
import korflab
from scipy.stats import pearsonr

def read_kmers(filename):
	kdict = {}
	with open(filename) as fp:
		for line in fp:
			kmer, prob = line.split()
			kdict[kmer] = float(prob)
	return kdict

parser = argparse.ArgumentParser(
	description='compute IMEter score for introns')
parser.add_argument('fasta', help='input fasta file')
parser.add_argument('prox', help='proximal kmer table')
parser.add_argument('dist', help='distal kmer table')
parser.add_argument('k', type=int, help='kmer size')
arg = parser.parse_args()

prox = read_kmers(arg.prox)
dist = read_kmers(arg.dist)

X = []
Y = []
for name, seq in korflab.readfasta(arg.fasta):
	score = 0
	for i in range(len(seq) - arg.k + 1):
		kmer = seq[i:i+arg.k]
		score += math.log2(prox[kmer] / dist[kmer])
	f = name.split()
	y = float(f[2][1:])
	Y.append(y)
	X.append(score)
	print(score, y, sep='\t')
p = pearsonr(X, Y)
print(p.statistic, p.pvalue, file=sys.stderr)
