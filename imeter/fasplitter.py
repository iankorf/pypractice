import argparse
import random
import korflab

parser = argparse.ArgumentParser(
	description='randomly split fasta file into 2 parts')
parser.add_argument('fasta', help='input fasta file')
parser.add_argument('out1', help='name of output file 1')
parser.add_argument('out2', help='name of output file 2')
arg = parser.parse_args()

with open(arg.out1, 'w') as fh1, open(arg.out2, 'w') as fh2:
	for name, seq in korflab.readfasta(arg.fasta):
		fh = fh1 if random.random() < 0.5 else fh2
		print(f'>{name}', seq, sep='\n', file=fh)
