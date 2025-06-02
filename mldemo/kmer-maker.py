import argparse
import itertools
import math
import re
import sys
import korflab

def readseqs(file, k):
	kmers = {}
	for t in itertools.product('ACGT', repeat=k):
		kmers[''.join(t)] = 1 # pseudo-count added
	total = 0
	with open(file) as fp:
		for line in fp:
			seq = line.rstrip()
			for i in range(len(seq) -k + 1):
				kmer = seq[i:i+k]
				if not re.match('^[ACGT]+$', kmer): continue
				if kmer not in kmers: continue
				total += 1
				kmers[kmer] += 1
	if len(kmers) != 4**k: sys.exit('k appears to be too high')
	kprob = {}
	for k, v in sorted(kmers.items()): kprob[k] = v/total
	return kprob

parser = argparse.ArgumentParser()
parser.add_argument('exons', help='file of exon sequences')
parser.add_argument('introns', help='file of intron sequences')
parser.add_argument('k', type=int, help='size of kmer')
arg = parser.parse_args()

kex = readseqs(arg.exons, arg.k)
kin = readseqs(arg.introns, arg.k)
for kmer in kex:
	print(kmer, math.log2(kex[kmer]/kin[kmer]))
