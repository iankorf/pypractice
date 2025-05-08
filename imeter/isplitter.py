import argparse
import korflab

parser = argparse.ArgumentParser(description='split introns based on position')
parser.add_argument('fasta', help='input fasta file')
parser.add_argument('split', type=int)
parser.add_argument('--high', action='store_true', help='keep high, not low')
arg = parser.parse_args()

for name, seq in korflab.readfasta(arg.fasta):
	f = name.split('|')
	beg, end = f[1].split('-')
	beg = int(beg)
	if arg.high:
		if beg > arg.split:
			print('>', name, sep='')
			print(seq)
	else:
		if beg <= arg.split:
			print('>', name, sep='')
			print(seq)
		