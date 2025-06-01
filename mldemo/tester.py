import argparse
import korflab

def readseq(file):
	with open(file) as fp:
		for line in fp: yield line.rstrip()

def readpwm(file):
	alph = 'ACGT'
	pwm = []
	with open(file) as fp:
		for line in fp:
			d = {}
			f = line.split()
			for nt, v in zip(alph, f):
				d[nt] = float(v)
			pwm.append(d)
	return pwm

def score_pwm(pwm, seq):
	s = 1
	for i, nt in enumerate(seq):
		s *= pwm[i][nt]
	return s

parser = argparse.ArgumentParser()
parser.add_argument('truepwm', help='pwm generated from real observations')
parser.add_argument('fakepwm', help='pwm generated from fake/decoy sites')
parser.add_argument('trueseq', help='true sites')
parser.add_argument('fakeseq', help='fake sites')
arg = parser.parse_args()

tpwm = readpwm(arg.truepwm)
fpwm = readpwm(arg.fakepwm)

tp = 0
fp = 0
tn = 0
fn = 0
for seq in readseq(arg.trueseq):
	true_score = score_pwm(tpwm, seq)
	fake_score = score_pwm(fpwm, seq)
	if true_score > fake_score: tp += 1
	else:                       fp += 1
	
for seq in readseq(arg.fakeseq):
	true_score = score_pwm(tpwm, seq)
	fake_score = score_pwm(fpwm, seq)
	if true_score > fake_score: fn += 1
	else:                       tn += 1

print('True Positives:', tp)
print('True Negatives:', tn)
print('False Positives:', fp)
print('False Negatives:', fn)
print('Accuracy:', (tp+tn) / (tp+tn+fp+fn))