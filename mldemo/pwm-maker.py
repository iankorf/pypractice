import argparse
import re
import korflab

def init_pwm(seq):
	pwm = []
	for _ in seq:
		pwm.append({'A':0, 'C':0, 'G':0, 'T':0})
	return pwm

parser = argparse.ArgumentParser()
parser.add_argument('seqs', help='file of sequences')
arg = parser.parse_args()

pwm = None
total = 0

with open(arg.seqs) as fp:
	for line in fp:
		seq = line.rstrip()
		if not re.search('^[ACGT]+$', seq): continue
		if pwm is None: pwm = init_pwm(seq)
		total += 1
		for i, nt in enumerate(seq):
			pwm[i][nt] += 1

for d in pwm:
	for k, v in d.items():
		print(f'{v/total:.4f}', end='\t')
	print()
