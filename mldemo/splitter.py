import argparse
import korflab

parser = argparse.ArgumentParser()
parser.add_argument('seqs', help='file of sequences')
parser.add_argument('splits', type=int, help='number of files to make')
parser.add_argument('name', help='file prefix')
arg = parser.parse_args()

for i in range(arg.splits):
	with open(arg.seqs) as fp, open(f'{arg.name}.{i}.txt', 'w') as ofp:
		for j, line in enumerate(fp):
			if i == j % arg.splits: print(line, end='', file=ofp)
		
