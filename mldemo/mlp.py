#!/usr/bin/env python3

import argparse
import gzip
import itertools
import random
import os
import statistics
import sys

import korflab

##############
## Classics ##
##############

def classic_algorithms(arg, train_func, score_func):
	"""Train and test classic/simple sequence models"""

	# read sequences and reformat
	seqs1 = [(1, seq) for name, seq in korflab.readfasta(arg.pos)]
	seqs0 = [(0, seq) for name, seq in korflab.readfasta(arg.neg)]
	if arg.limit: seqs = seqs1[:arg.limit] + seqs0[:arg.limit]
	else:         seqs = seqs1 + seqs0
	random.shuffle(seqs)

	# cross-validation splitting
	accs = []
	for train, test in korflab.cross_validation(seqs, arg.xvalid):

		# make pwms from seqs
		trues = [seq for label, seq in train if label == 1]
		fakes = [seq for label, seq in train if label == 0]
		twam = train_func(trues, arg)
		fwam = train_func(fakes, arg)

		# score vs. test set
		tp, tn, fp, fn = 0, 0, 0, 0
		for entry in test:
			label, seq = entry
			tscore = score_func(twam, arg.order, seq)
			fscore = score_func(fwam, arg.order, seq)

			if label == 1:
				if tscore > fscore: tp += 1
				else:               fn += 1
			else:
				if fscore > tscore: tn += 1
				else:               fp += 1
		acc = (tp + tn) / (tp + tn + fp + fn)
		accs.append(acc)
		print(tp, tn, fp, fn, acc, file=sys.stderr, flush=True)

	return statistics.mean(accs)

def make_wam(seqs, arg):

	order = arg.order
	length = len(seqs[0])

	# create the data structures
	alph = 'ACGT'
	count = []
	freq = []
	for i in range(length):
		d = {}
		f = {}
		for tup in itertools.product(alph, repeat=order):
			s = ''.join(tup)
			d[s] = {}
			f[s] = {}
			for nt in alph:
				d[s][nt] = 0
				f[s][nt] = None
		count.append(d)
		freq.append(f)

	# do the actual counting
	total = 0
	for seq in seqs:
		total += 1
		for i in range(order, len(seq)):
			ctx = seq[i-order:i]
			nt = seq[i]
			count[i][ctx][nt] += 1

	# convert to freqs
	for i in range(length):
		for ctx in count[i]:
			tot = sum(count[i][ctx].values())
			for nt in count[i][ctx]:
				if tot == 0: freq[i][ctx][nt] = 0 # maybe None
				else: freq[i][ctx][nt] = count[i][ctx][nt] / tot

	return freq

def score_wam(wam, order, seq):
	p = 1
	for i in range(order, len(seq)):
		ctx = seq[i-order:i]
		nt = seq[i]
		p *= wam[i][ctx][nt]
	return p

def make_nmm(seqs, arg):
	k = arg.order
	count = {}
	total = 0
	for seq in seqs:
		for i in range(len(seq) -k + 1):
			kmer = seq[i:i+k]
			if kmer not in count: count[kmer] = 0
			count[kmer] += 1
			total += 1
	freq = {}
	for kmer in count:
		freq[kmer] = count[kmer] / total
	return freq

def score_nmm(nmm, k, seq):
	score = 1
	for i in range(len(seq) -k +1):
		kmer = seq[i:i+k]
		score *= nmm[kmer]
	return score

def run_pwm(arg):
	arg.order = 0 # yes, a pwm is just a 0th order wam
	return classic_algorithms(arg, make_wam, score_wam)

def run_wam(arg):
	return classic_algorithms(arg, make_wam, score_wam)

def run_nmm(arg):
	return classic_algorithms(arg, make_nmm, score_nmm)

###########
## Torch ##
###########

def run_mlp(arg):

	from numpy import vstack
	from pandas import read_csv

	from sklearn.preprocessing import LabelEncoder
	from sklearn.metrics import accuracy_score, f1_score

	import torch
	from torch.utils.data import Dataset
	from torch.utils.data import DataLoader
	from torch.utils.data import random_split
	from torch import Tensor
	from torch.nn import Linear
	from torch.nn import ReLU
	from torch.nn import Sigmoid
	from torch.nn import Module, ModuleList
	from torch.optim import SGD
	from torch.nn import BCELoss
	from torch.nn.init import kaiming_uniform_
	from torch.nn.init import xavier_uniform_

	class CSVDataset(Dataset):

		def __init__(self, path):
			df = read_csv(path, header=None) # load the csv file as a dataframe
			self.X = df.values[:, :-1] # store the inputs
			self.y = df.values[:, -1]  # and outputs
			self.X = self.X.astype('float32') # ensure input data is floats
			self.y = LabelEncoder().fit_transform(self.y) # label target
			self.y = self.y.astype('float32') # ensure floats
			self.y = self.y.reshape((len(self.y), 1))

		def __len__(self):
			return len(self.X)

		def __getitem__(self, idx):
			return [self.X[idx], self.y[idx]]

		def get_splits(self, n_test):
			test_size = round(n_test * len(self.X))
			train_size = len(self.X) - test_size
			return random_split(self, (train_size, test_size))

	class MLP(Module):

		def __init__(self, n_inputs, layers):
			super(MLP, self).__init__()

			self.hidden = ModuleList()
			self.act = ModuleList()
			for i in range(1, len(layers)):
				input = layers[i-1]
				output = layers[i]
				self.hidden.append(Linear(input, output))

			for i in range(len(self.hidden) -1):
				kaiming_uniform_(self.hidden[i].weight, nonlinearity='relu')
				self.act.append(ReLU())
			xavier_uniform_(self.hidden[-1].weight)
			self.act.append(Sigmoid())

		def forward(self, X):
			for hidden, act in zip(self.hidden, self.act):
				X = hidden(X)
				X = act(X)
			return X

	def prepare_data(path, split):
		dataset = CSVDataset(path)
		train, test = dataset.get_splits(split)
		# why are the batch sizes hard-coded?
		train_dl = DataLoader(train, batch_size=32, shuffle=True)
		test_dl = DataLoader(test, batch_size=1024, shuffle=False)
		return train_dl, test_dl

	def train_model(train_dl, model, r, m):
		criterion = BCELoss() # or CrossEntropyLoss, MSELoss
		optimizer = SGD(model.parameters(), lr=r, momentum=m) # or Adam
		for epoch in range(50):
			for i, (inputs, targets) in enumerate(train_dl): # mini batches
				optimizer.zero_grad() # clear the gradients
				yhat = model(inputs) # compute the model output
				loss = criterion(yhat, targets) # calculate loss
				loss.backward() # credit assignment
				optimizer.step() # update model weights

	def evaluate_model(test_dl, model):
		predictions, actuals = list(), list()
		for i, (inputs, targets) in enumerate(test_dl):
			yhat = model(inputs) # evaluate the model on the test set
			yhat = yhat.detach().numpy() # retrieve numpy array
			actual = targets.numpy()
			actual = actual.reshape((len(actual), 1))
			yhat = yhat.round() # round to class values
			predictions.append(yhat) # store
			actuals.append(actual)

		predictions, actuals = vstack(predictions), vstack(actuals)
		acc = accuracy_score(actuals, predictions)
		f1 = f1_score(actuals, predictions, average='weighted')
		return acc, f1

	def predict(row, model):
		row = Tensor([row]) # convert row to data (can be tuple)
		yhat = model(row) # make prediction
		yhat = yhat.detach().numpy() # retrieve numpy array
		return yhat

	if arg.seed: torch.manual_seed(arg.seed)

	# read fasta files and convert to a single one-hot encoded csv
	s1 = korflab.ntencoder(arg.pos, label='1')
	s0 = korflab.ntencoder(arg.neg, label='0')
	if arg.limit: seqs = s1[:arg.limit] + s0[:arg.limit]
	else:         seqs = s1 + s0
	random.shuffle(seqs)
	csv = f'temp.{os.getpid()}.csv'
	with open(csv, 'w') as fp:
		for item in seqs:
			fp.write(','.join(item))
			fp.write('\n')
	size = len(s1[0]) -1 # length of sequence

	# check network architecture
	if len(arg.layers) < 2: raise Exception('need at least 2 layers')
	if arg.layers[0] != size: raise Exception('input layer != inputs')
	if arg.layers[-1] != 1: raise Exception('last layer must be 1')

	# train, test, evaluate model
	accs = []
	for i in range(arg.xvalid):
		train_dl, test_dl = prepare_data(csv, 0.25)
		model = MLP(size, arg.layers)
		train_model(train_dl, model, arg.rate, arg.momentum)
		acc, f1 = evaluate_model(test_dl, model)
		print(f'{acc:.3f}', file=sys.stderr, flush=True)
		accs.append(acc)

	if arg.save != None: torch.save(model.state_dict(), arg.save)

	# report aggregate performance
	os.remove(csv)
	return statistics.mean(accs)

#####################
# Environment Check #
#####################

ENV = """\
name: mldemo
channels:
  - conda-forge
  - defaults
dependencies:
  - python
  - pytorch
  - pandas
  - scikit-learn"""

if os.environ.get('CONDA_DEFAULT_ENV') != 'mldemo':
	print(ENV)
	sys.exit(f'\nERROR: create and activate mldemo environment first!')

#########
## CLI ##
#########

parser = argparse.ArgumentParser(
	description='fun with various sequence model architectures')
parser.add_argument('--limit', type=int, metavar='<int>',
	help='limit the data set size to this amount for testing')
parser.add_argument('--xvalid', type=int, default=4, metavar='<int>',
	help='x-fold cross-validation [%(default)s]')
sub = parser.add_subparsers(required=True, help='sub-commands')

## pwm ##
sub_pwm = sub.add_parser('pwm', help='position weight matrix')
sub_pwm.add_argument('pos', help='positive, real sequences')
sub_pwm.add_argument('neg', help='negative, fake sequences')
sub_pwm.set_defaults(func=run_pwm)

## wam ##
sub_wam = sub.add_parser('wam', help='weight array matrix')
sub_wam.add_argument('pos', help='positive, real sequences')
sub_wam.add_argument('neg', help='negative, fake sequences')
sub_wam.add_argument('--order', required=False, type=int, default=1,
	metavar='<int>', help='order of Markov model [%(default)i]')
sub_wam.set_defaults(func=run_wam)

## nmm ##
sub_nmm = sub.add_parser('nmm', help='nth-order Markov model')
sub_nmm.add_argument('pos', help='positive, real sequences')
sub_nmm.add_argument('neg', help='negative, fake sequences')
sub_nmm.add_argument('--order', required=False, type=int, default=4,
	metavar='<int>', help='order of Markov model [%(default)i]')
sub_nmm.set_defaults(func=run_nmm)

## mlp ##
sub_mlp = sub.add_parser('mlp', help='multi-layer perceptron')
sub_mlp.add_argument('pos', help='positive, real sequences')
sub_mlp.add_argument('neg', help='negative, fake sequences')
sub_mlp.add_argument('layers', type=int, nargs='*', metavar='<int>',
	help='nodes in each hidden layer, e.g. 168 42 21 1')
sub_mlp.add_argument('--rate', type=float, default=0.01,
	metavar='<float>', help='learning rate [%(default)f]')
sub_mlp.add_argument('--momentum', type=float, default=0.9,
	metavar='<float>', help='momentum [%(default)f]')
sub_mlp.add_argument('--seed', type=int, metavar='<int>',
	help='set random seed')
sub_mlp.add_argument('--save', type=str, metavar='<path>',
	help='where to save the model', default=None)
sub_mlp.set_defaults(func=run_mlp)

## finish up ##
arg = parser.parse_args()
perf = arg.func(arg)
print('accuracy:', perf)

