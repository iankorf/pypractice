import argparse
import gzip
import sys
import korflab


parser = argparse.ArgumentParser()
parser.add_argument('fasta')
parser.add_argument('gff')
parser.add_argument('--min-intron', type=int, default=60,
	help='minimum intron length [%(default)i]')
parser.add_argument('--max-intron', type=int, default=600,
	help='maximum intron length [%(default)i]')
arg = parser.parse_args()

genome = {}
fp = korflab.getfp(arg.gff)
for line in fp:
	if line.startswith('#'): continue
	f = line.split('\t')
	if f[2] != 'exon': continue
	chrom = f[0]
	if chrom not in genome: genome[chrom] = {}
	tid = f[8].split(';')[2][7:]
	if tid not in genome[chrom]: genome[chrom][tid] = []
	genome[chrom][tid].append({
		'beg': int(f[3]),
		'end': int(f[4]),
		'str': f[6]})

seq2gff = {
	'1': 'Chr1',
	'2': 'Chr2',
	'3': 'Chr3',
	'4': 'Chr4',
	'5': 'Chr5',
	'mitochondria': 'ChrM',
	'chloroplast': 'ChrC'
}

seen = set()
for defline, seq in korflab.readfasta(arg.fasta):
	f = defline.split()
	chrom = seq2gff[f[0]]
	for tid, exons in genome[chrom].items():
		gmin = exons[0]['beg']
		gmax = exons[-1]['end']
		flip = False
		introns = []
		for i in range(1, len(exons)):
			ib = exons[i-1]['end'] +1
			ie = exons[i]['beg'] -1
			ilength = ie - ib + 1
			if ilength < arg.min_intron: continue
			if ilength > arg.max_intron: continue
			iseq = seq[ib-1:ie]
			if iseq in seen: continue
			seen.add(iseq)
			if exons[i]['str'] == '+':
				rb = ib - gmin + 1
				re = ie - gmin + 1
				N = i
			else:
				flip = True
				iseq = korflab.anti(iseq)
				re = gmax - ib + 1
				rb = gmax - ie + 1
				N = len(exons) - i
			S = 'FORWARD' if exons[i]['str'] == '+' else 'REVERSE'
			L = ie - ib +1
			introns.append((f'>{tid}-{N}|{rb}-{re}|{chrom}:{ib}-{ie} {S} LENGTH={L}', iseq))
		if len(introns) == 0: continue
		if flip: introns.reverse()
		for defline, iseq in introns:
			print(defline)
			for i in range(0, len(iseq), 80):
				print(iseq[i:i+80])
