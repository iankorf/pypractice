import argparse
import korflab

def readseq(file):
	with open(file) as fp:
		for line in fp: yield line.rstrip()

def score_model(model, seq, k):
	s = 0
	for i in range(len(seq) -k + 1):
		kmer = seq[i:i+k]
		if kmer in model: s += model[kmer]
	return s

parser = argparse.ArgumentParser()
parser.add_argument('model', help='exon-intron log-odds model')
parser.add_argument('exons', help='exons')
parser.add_argument('introns', help='introns')
arg = parser.parse_args()

model = {}
k = None
with open(arg.model) as fp:
	for line in fp:
		kmer, val = line.split()
		model[kmer] = float(val)
		if k is None: k = len(kmer)

tp = 0
fp = 0
tn = 0
fn = 0
for seq in readseq(arg.exons):
	s = score_model(model, seq, k)
	if s > 0: tp += 1
	else:     fn += 1

for seq in readseq(arg.introns):
	s = score_model(model, seq, k)
	if s > 0: fp += 1
	else:     tn += 1

print('True Positives:', tp)
print('True Negatives:', tn)
print('False Positives:', fp)
print('False Negatives:', fn)
print('Accuracy:', (tp+tn) / (tp+tn+fp+fn))
