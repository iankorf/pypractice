import argparse
import random
import korflab

parser = argparse.ArgumentParser(
	description='scramble sequences in a FASTA file')
parser.add_argument('fasta', help='input fasta file')
arg = parser.parse_args()

for name, seq in korflab.readfasta(arg.fasta):
	print('>', name, sep='')
	lseq = list(seq)
	random.shuffle(lseq)
	print(''.join(lseq))
