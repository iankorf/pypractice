import argparse
import math
import korflab

def readkmers(filename):
	kdict = {}
	with open(filename) as fp:
		for line in fp:
			kmer, prob = line.split()
			kdict[kmer] = float(prob)
	return kdict

parser = argparse.ArgumentParser(description='compare kmer probabilities')
parser.add_argument('file1', help='input kmer file 1')
parser.add_argument('file2', help='input kmer file 2')
arg = parser.parse_args()

k1 = readkmers(arg.file1)
k2 = readkmers(arg.file2)

dkl = 0
dtc = 0
for kmer in k1:
	dkl += k1[kmer] * math.log2(k1[kmer] / k2[kmer])
	dtc += abs(k1[kmer] - k2[kmer])

print(dkl, dtc)