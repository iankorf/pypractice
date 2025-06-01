import argparse
import random
import korflab


parser = argparse.ArgumentParser()
parser.add_argument('introns', help='fasta file of introns')
parser.add_argument('seqs', type=int, help='number of sequences to make')
parser.add_argument('size', type=int, help='length of decoy site')
parser.add_argument('--donor', action='store_true',
	help='make donor sites')
parser.add_argument('--acceptor', action='store_true',
	help='make acceptor sites')
parser.add_argument('--anti', action='store_true',
	help='generate from opposite strand')
arg = parser.parse_args()

sites = []
for defline, seq in korflab.readfasta(arg.introns):
	if arg.anti: seq = korflab.anti(seq)
	for i in range(20, len(seq) -20):
		if arg.donor:
			if seq[i:i+2] == 'GT': sites.append(seq[i:i+arg.size])
		elif arg.acceptor:
			if seq[i:i+2] == 'AG': sites.append(seq[i-arg.size:i])

random.shuffle(sites)
for i in range(arg.seqs): print(sites[i])