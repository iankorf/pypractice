import argparse
import gzip
import re
import sys
import korflab


parser = argparse.ArgumentParser()
parser.add_argument('fasta')
parser.add_argument('gff')
parser.add_argument('--min-intron', type=int, default=60,
	help='minimum intron length [%(default)i]')
parser.add_argument('--max-intron', type=int, default=600,
	help='maximum intron length [%(default)i]')
parser.add_argument('--min-exon', type=int, default=30,
	help='minimum exon length [%(default)i]')
parser.add_argument('--max-exon', type=int, default=1000,
	help='maximum exon length [%(default)i]')
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

		# skip over genes with non-canonical lengths
		skip = False
		for exon in exons:
			if exon['end'] - exon['beg'] < arg.min_exon:
				skip = True
				break
			if exon['end'] - exon['beg'] > arg.max_exon:
				skip = True
				break
			
		if skip: continue
		for i in range(1, len(exons)):
			ib = exons[i-1]['end'] +1
			ie = exons[i]['beg'] -1
			if ie - ib < arg.min_intron:
				skip = True
				break
			if ie - ib > arg.max_intron:
				skip = True
				break
		if skip: continue
		
		for exon in exons:
			eseq = seq[exon['beg']-1:exon['end']]
			if eseq in seen: continue
			seen.add(eseq)
			if exon['str'] == '+': eseq = korflab.anti(eseq)
			if not re.match('^[ACGT]+$', eseq): continue
			print('EXON:', eseq)
				
		for i in range(1, len(exons)):
			ib = exons[i-1]['end'] +1
			ie = exons[i]['beg'] -1
			iseq = seq[ib-1:ie]
			if not re.match('^[ACGT]+$', iseq): continue
			if exons[i]['str'] == '-': iseq = korflab.anti(iseq)
			if not iseq.startswith('GT'): continue
			if not iseq.endswith('AG'): continue
			if iseq in seen: continue
			seen.add(iseq)
			print('INTRON:', iseq)