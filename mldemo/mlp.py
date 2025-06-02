#!/usr/bin/env python3

import argparse
import gzip
import itertools
import random
import os
import statistics
import sys

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

def ntencoder(file, label=None, binary=False):
	"""One-hot/binary encodes a sequence file, optionally with terminal label"""
	encoding = {'A':'0001', 'C':'0010', 'G':'0100', 'T':'1000'}
	if binary: encoding = {'A':'00', 'C':'01', 'G':'10', 'T':'11'}

	data = []
	with open(file) as fp:
		for line in fp:
			seq = line.rstrip()
			s = [encoding[nt] for nt in seq]
			s = ''.join(s)
			if label: s += str(label)
			data.append(s)
	return data

def cross_validation(seqs, x):
	"""Generates cross-validation sets"""
	for i in range(x):
		train = []
		test = []
		for j in range(len(seqs)):
			if j % x == i: test.append(seqs[j])
			else:          train.append(seqs[j])
		yield train, test


#########
## CLI ##
#########

parser = argparse.ArgumentParser(
	description='fun with neural networks')
parser.add_argument('pos', help='positive, real sequences')
parser.add_argument('neg', help='negative, fake sequences')
parser.add_argument('layers', type=int, nargs='*', metavar='<int>',
	help='nodes in each hidden layer, e.g. 40 1 or 200 1')
parser.add_argument('--limit', type=int, metavar='<int>',
	help='limit the data set size to this amount for testing')
parser.add_argument('--xvalid', type=int, default=2, metavar='<int>',
	help='x-fold cross-validation [%(default)s]')
parser.add_argument('--rate', type=float, default=0.01,
	metavar='<float>', help='learning rate [%(default)f]')
parser.add_argument('--momentum', type=float, default=0.9,
	metavar='<float>', help='momentum [%(default)f]')
parser.add_argument('--seed', type=int, metavar='<int>',
	help='set random seed')
parser.add_argument('--save', type=str, metavar='<path>',
	help='where to save the model', default=None)
arg = parser.parse_args()

if arg.seed: torch.manual_seed(arg.seed)

# read sequence files and convert to a single one-hot encoded csv
s1 = ntencoder(arg.pos, label='1')
s0 = ntencoder(arg.neg, label='0')
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
print(statistics.mean(accs))



