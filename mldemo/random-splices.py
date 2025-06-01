import argparse
import korflab

parser = argparse.ArgumentParser()
parser.add_argument('seqs', type=int, help='number of sequences to generate')
parser.add_argument('size', type=int, help='length of sequence')
parser.add_argument('--donor', action='store_true',
	help='start with GT...')
parser.add_argument('--acceptor', action='store_true',
	help='end with ...AG')
arg = parser.parse_args()

for _ in range(arg.seqs):
	size = arg.size
	if arg.donor: size -= 2
	if arg.acceptor: size -= 2
	seq = korflab.random_dna(size)
	if arg.donor: seq = 'GT' + seq
	if arg.acceptor: seq = seq + 'AG'
	print(seq)
	