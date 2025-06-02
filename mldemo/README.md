Sequence Patterns Machine Learning Demo
=======================================

In this unit, you will explore several ways to get a computer to recognize the
parts of a gene (exon, intron, splice sites). In other words, you're going to
teach a computer how to "read the book of life". In genomic sequence, there
tend to be 2 kinds of "features".

1. Fixed length features, like splice sites
2. Variable length features, like exons and introns

To model fixed length features, specifically splice donor and splice acceptor
sites, we will use Position Weight Matrices. For variable length features, we
will use kmers.

Both of these constructs are familiar to you. When we built the IMEter, that
was a kmer model. When we found the motifs present in high scoring introns with
MEME, those motifs were position weight matrices.

To create these models, we need exon and intron sequences. You can find these
in the directory as `cds.fa.gz` (coding sequence) and `introns.fa.gz`. Both of
these come from A. thaliana.

## Splice Sites ##

Splice donor sites are at the start of introns. Splice acceptor sites are at
the end of introns.

### True Sites

Extract the donor and acceptor sites as follows:

```
python3 splices.py introns.fa.gz
```

This results in 2 files: `acc.txt` and `don.txt`. Use `less` to examine the
files and you will find the sequences are all 10 nt long. The file names and
the number 10 are default parameters of the program, but these can be
overridden with commandline options. When you write your own programs, do not
hard-code paths or parameters unless you also provide a way to override them,
like this program does.

How many sequences are there? (hint: use `wc`). Did you notice this isn't the
same number as the input sequences? Can you figure out why that is? Try reading
the program.

How many unique sequences are there? (hint: use `sort -u`). Fewer. Do you think
it's a good idea to remove duplicates?

-----

To visualize the donor and acceptor sites as a position weight matrix, first
create a subset of sequences that is smaller. (hint: use `head -1000`). Then
load your file into WebLogo (https://weblogo.berkeley.edu/logo.cgi).

Next, try sorting the file before you put it into WebLogo.

```
sort acc.txt | head -1000 > whatever
```

If you subset a dataset, you might be biasing it in some way if it already has
some _structure_. For example, what if the first 1000 splice sites correspond
to a specific class of genes that are all right next to each other in the file.
Your PWMs might represent those sequences better than others. For this reason,
you should randomize sequences before making a subset. The `splices.py` program
does this automatically.

Run `splice.py` again, this time with a limit of 20,000 sequences. 20k is still
a lot of splices.

```
python3 splices.py introns.fa.gz --limit 20000
```

-----

To create a PWM, run `pwm-maker.py`.

```
python3 pwm-maker.py don.txt
python3 pwm-maker.py acc.txt
```

The output is basically the same as WebLogo but in numeric form.

### Fake Sites

When you make a _model_ of something, the model represents a mathematical
idealization of the data. It represents what you expect to see in the future.
But how well does the model actually work at predicting the future? To start
answering this question, we need some fake/decoy sites. We need to be able to
ask "does some new observation look more like a real site or a fake site?" We
know where to get real sites (previous genome annotation), but where do we get
fake sites?

We often compare _things_ to a random model, so it seems like generating random
sequences is an okay place to start. But random sequences lack biological
context. Another source of data _should_ be biological. What sequences are
definitely not splice sites? That turns out to be a difficult question.
Alternative splicing exists, some of the sites we might choose (e.g in the
middle of an intron), might be alternative splice sites.

We will make 2 kinds of fake data.

- randomly generated sites
- GT and AG sites from inside introns

Here's how to make random donor and acceptor sites:

```
python3 random-splices.py 10 10 --donor
python3 random-splices.py 10 10 --acceptor
```

Here's how to sample sites inside introns:

```
python3 decoy-splices.py introns.fa.gz 10 10 --donor
python3 decoy-splices.py introns.fa.gz 10 10 --acceptor
```

### Training

The biggest no-no of machine learning is testing and training on the same data.
You should do all of your development on a training set and then once
everything is done, you use the testing set to examine how well you did. To
split files into distinct groups, use the `splitter.py` program.

```
python3 splitter.py acc.txt 2 acc
python3 splitter.py don.txt 2 don
```

Your files are now split into 2 equal parts.

- `acc.0.txt` training for acceptors
- `acc.1.txt` testing for acceptors
- `don.0.txt` training for donors
- `don.1.txt` testing for donors

Make PWMs for the training sets.

```
python3 pwm-maker.py acc.0.txt > acc.0.pwm
python3 pwm-maker.py don.0.txt > don.0.pwm
```

Also make fake sequences.  These will be split into 2 sets, just like the
normal data. Let's make 20K of each and that will split into 10k.

```
python3 random-splices.py 20000 10 --donor > don.random.txt
python3 random-splices.py 20000 10 --acceptor > acc.random.txt
python3 decoy-splices.py introns.fa.gz 20000 10 --donor > don.decoy.txt
python3 decoy-splices.py introns.fa.gz 20000 10 --acceptor > acc.decoy.txt

python3 splitter.py don.random.txt 2 don.random
python3 splitter.py acc.random.txt 2 acc.random
python3 splitter.py don.decoy.txt 2 don.decoy
python3 splitter.py acc.decoy.txt 2 acc.decoy
```

Now, generate PWMs for the fake sequences.

```
python3 pwm-maker.py acc.random.0.txt > acc.random.0.pwm
python3 pwm-maker.py don.random.0.txt > don.random.0.pwm
python3 pwm-maker.py acc.decoy.0.txt > acc.decoy.0.pwm
python3 pwm-maker.py don.decoy.0.txt > don.decoy.0.pwm
```

### Testing

Now that we have some models trained, it's time to see if they work.

```
python3 pwm-tester.py don.0.pwm don.random.0.pwm don.1.txt don.random.1.txt
python3 pwm-tester.py don.0.pwm don.decoy.0.pwm don.1.txt don.decoy.1.txt
python3 pwm-tester.py acc.0.pwm acc.random.0.pwm acc.1.txt acc.random.1.txt
python3 pwm-tester.py acc.0.pwm acc.decoy.0.pwm acc.1.txt acc.decoy.1.txt
```

Weirdly, donor and acceptor don't behave the same. It's easier to discriminate
between real donors and decoy (intron) donors, than real donors and random
donors. Is this because introns don't want to have anything that looks like a
donor because it might cause splicing? But for acceptors this is not true.
There isn't that much difference discriminating between random acceptors and
decoy acceptors, and random is actually easier. Do you think this might be true
of all genomes?


## Exons and Introns ##

Even though exons and introns are variable length features, for the purposes of
this exercise, we are going to make them fixed length (for reasons you will see
later). Run the following command lines to sample the exon and intron sequences
and create files of fixed length sequence.

```
python3 exon-intron.py cds.fa.gz 20000 > exons.txt
python3 exon-intron.py introns.fa.gz 20000 > introns.txt
```

Once again, we will split these into testing and training sets.

```
python3 splitter.py exons.txt 2 exons
python3 splitter.py introns.txt 2 introns
```

Now it's time to build the model.

```
python3 kmer-maker.py exons.0.txt introns.0.txt 4 > exon-vs-intron.4.kmer
```

Examine the `exon-intron.kmer4` file with `less`. Instead of a file of
probabilities (which was used for PWMs), this is a file of log-odss ratios. A
positive number means the sequence is more likely to occur in exons than
introns. A negative number is the reverse. It's just like the IMEter.

Let's see if it works.

```
python3 kmer-tester.py exon-vs-intron.4.kmer exons.1.txt introns.1.txt
```

## Cross-Validation ##

In the experiments above, you trained a model on training data and tested it on
testing data. While you're not allowed to train and test on the same data, you
are allowed to swap positions of testing and training. That is, you can perform
the whole operation twice and take the average of the two performance figures.
This is useful when data is limiting. You can extend this concept to multiple
data splits.

- no cross-validation (what we did)
	- train: set1
	- test: set2
- 2-fold cross-validation (swap training and testing)
	- run 1:
		- train: set1
		- test: set2
	- ru 2:
		- train: set2
		- test: set1
- 3-fold cross-validation (train on more data than test)
	- run 1:
		- train: set1 + set2
		- test: set3
	- run 2:
		- train: set1 + set3
		- test: set2
	- run 3:
		- train: set2 + set3
		- test: set1


## Automation and Experimentation ##

- Can you automate the training and testing of PWMs?
- Can you automate 2-fold cross-validation?
- Can you make this tidy (keep files in 1 directory)?
- Can you do the same for kmers?

Questions:

- What is the optimal size for k in exons vs. introns?
- What happens if you test and train on the same data?
- Would a PWM model work for exons and introns?
- Would a kmer model work for splice sites?


## Perceptron ##

Neural networks are popular for many kinds of machine learning tasks. Let's
build and test a neural network to recognize sequence features.

The program we will use is called `mlp.py`. It's a little complicated to
explain the code, but the usage is relatively simple.

```
python3 mlp.py
```

You must give the program 2 files, a file of true sequences and a file of fake
sequences. It will therefore work with the files you have already made.

The next arguments are the "shape" of the neural network. For the splice site
experiments that are 10 nt long, the first dimension maps the nucleotides to
states with one-hot encoding. If there are 10 nts, there are 40 input states.
The last dimension must be 1. So here's how to run one of the splice site
experiments.

```
python3 mlp.py acc.txt acc.random.txt 40 1
```

The program automatically does x-fold cross-validation. For 2-fold (default) it
reports the accuracy twice (to stderr) and then reports the average accuracy
(to stdout).

We can build a perceptron to recognize exons and introns also. We only need to
change the input files and then change the first layer to match the 50 nt long
sequences.

```
python3 mlp.py exons.txt introns.txt 200 1
```

### Multi-layer Perceptron ###

To make a multi-layer perceptron, create layers between the input and output
layers.

```
python3 mlp.py acc.txt acc.random.txt 40 10 1
python3 mlp.py exons.txt introns.txt 200 20 1
```

Adding "hidden" layers between the input and output layers sometimes makes a
neural network perform much better. But not always. "Tuning" a neural network
for optimal perfomance requires modifying the hidden layers as well as a large
numbe of other "hyper-parameters".

## Shootout ##

Which models work best for which kinds of sequences?

Do you think your interpretation will hold up if you change genomes?
