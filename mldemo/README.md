Sequence Patterns Machine Learning Demo
=======================================

In this unit, you will explore several ways to get a computer to recognize the
parts of a gene (exon, intron, splice sites). It's sort of like teaching a
computer how to "read the book of life"! In genomic sequence, there tend to be
2 kinds of "features".

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

Splice donor sites are at the start of introns, and have the consensus `GTAAG`.
Splice acceptor sites are at the end of introns and have the consensus
`TTTCAG`.

### True Sites

Examine the `introns.fa.gz` file with `zless`.

```
zless introns.fa.gz
```

Note that the introns start with `GT` and end with `AG`.  Next, let's see how
many there are.

```
gunzip -c introns.fa.gz| grep -c ">"
```

If that sounds like a familiar number, this is the same set of unique introns
used in the previous imeter project. Extract the donor and acceptor sites as
follows:

```
python3 splices.py introns.fa.gz
```

This results in 2 files: `acc.txt` and `don.txt`. Use `less` to examine the
files and you will find the sequences are all 10 nt long. The file names and
the number 10 are default parameters of the `splices.py` program, but these can
be overridden with commandline options. When you write your own programs, do
not hard-code paths or parameters unless you also provide a way to override
them, like this program does.

How many sequences are there?

```
wc don.txt
wc acc.txt
```

Did you notice this isn't the same number as the input sequences? Can you guess
why? Try reading the program and see if that helps you decide.

How many unique sequences are there? (hint: use `sort -u`). Fewer. Do you think
it's a good idea to remove duplicates?

-----

To visualize the donor and acceptor sites as a position weight matrix, first
create a subset of sequences that is smaller. The website we're going to use
will break with a large file.

```
head -1000 don.txt > don-sample.txt
head -1000 acc.txt > acc-sample.txt
```

Now upload (or copy-paste) the sequences into the WebLogo website.
https://weblogo.berkeley.edu/logo.cgi

Whenver you create a subset of something, you risk making a biased sample. To see this clearly, try sorting before making the logo.

```
sort don.txt | head -1000 > don-sorted.txt
sort acc.txt | head -1000 > acc-sorted.txt
```

Load those into WebLogo and you will find a highly biased pattern. Whenever you
subset a dataset, you might be biasing it in some way if it already has some
_structure_. For example, what if the first 1000 splice sites correspond to a
specific class of genes that are all right next to each other in the file. Your
PWMs might represent those sequences better than others. For this reason, you
should randomize sequences before making a subset. The `splices.py` program
does this automatically.

Run `splice.py` again, this time with a limit of 20,000 sequences. 20k is still
a lot of splices, and it will make some of our tasks faster.

```
python3 splices.py introns.fa.gz --limit 20000
```

-----

To create a PWM, run `pwm-maker.py`.

```
python3 pwm-maker.py don.txt
python3 pwm-maker.py acc.txt
```

The output is basically the same as WebLogo, but in numeric form.

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
Alternative splicing exists. Some of the sites we might choose (e.g in the
middle of an intron), might be alternative splice sites. What other forms of
non-splice sites might work?

- GT and AG sites from exons
- GT and AG sites from the opposite strand
- GT and AG sites from intergenic sequence

All of these have issues. Exons are typically GC-rich compared to introns.
Sites on the opposite strand of introns will have the same GC-composition, but
the As and Ts will be swapped (and the Gs and Cs). If composition is
asymmetric, the opposite strand isn't a good model of fake splice sites or
introns in general. Intergenic sequence might be okay, except that it's not
transcribed, and so it may have different properties. Caveats aside, we will
make 2 kinds of fake data.

- randomly generated sites
- GT and AG sites from inside introns, which we call "decoy" sites

Here's how to make random donor and acceptor sites:

```
python3 random-splices.py 10 10 --donor
python3 random-splices.py 10 10 --acceptor
```

Here's how to make decoy donor and acceptor sites:

```
python3 decoy-splices.py introns.fa.gz 10 10 --donor
python3 decoy-splices.py introns.fa.gz 10 10 --acceptor
```

Take a look at the code for each program. Do you understand exactly how they
work? If not, call an instructor over to help.

### Training

The biggest no-no of machine learning is testing and training on the same data.
You should do all of your model building on a training set. Once everything is
done, you use the testing set to examine how well you did. To split files into
distinct groups, use the `splitter.py` program.

```
python3 splitter.py don.txt 2 don
python3 splitter.py acc.txt 2 acc
```

Your files are now split into 2 equal parts.

- `don.0.txt` training for donors
- `don.1.txt` testing for donors
- `acc.0.txt` training for acceptors
- `acc.1.txt` testing for acceptors

Make PWMs for the training sets. Examine them with `less`. You should see the
`GT` and `AG` in the PWMs as 1.000 probabilities.

```
python3 pwm-maker.py don.0.txt > don.0.pwm
python3 pwm-maker.py acc.0.txt > acc.0.pwm
```

Make random/decoy sequences. Examine the files with `less` to make sure they
look like they should. The donors should all begin with `GT` and the acceptors
should all end with `AG`.

```
python3 random-splices.py 20000 10 --donor > don.random.txt
python3 decoy-splices.py introns.fa.gz 20000 10 --donor > don.decoy.txt
python3 random-splices.py 20000 10 --acceptor > acc.random.txt
python3 decoy-splices.py introns.fa.gz 20000 10 --acceptor > acc.decoy.txt
```

We need to split these into training and testing sets also.

```
python3 splitter.py don.random.txt 2 don.random
python3 splitter.py don.decoy.txt 2 don.decoy
python3 splitter.py acc.random.txt 2 acc.random
python3 splitter.py acc.decoy.txt 2 acc.decoy
```

Now, generate PWMs for the fake sequences.

```
python3 pwm-maker.py don.random.0.txt > don.random.0.pwm
python3 pwm-maker.py don.decoy.0.txt > don.decoy.0.pwm
python3 pwm-maker.py acc.random.0.txt > acc.random.0.pwm
python3 pwm-maker.py acc.decoy.0.txt > acc.decoy.0.pwm
```

Take a look at all the files you made with `less`. Make sure all of the files
contain what you expect. If something seems amiss, stop now and discuss with
your lab partner or the instructors.

### Testing

Now that we have some models trained, it's time to see if they work.

```
python3 pwm-tester.py don.0.pwm don.random.0.pwm don.1.txt don.random.1.txt
python3 pwm-tester.py don.0.pwm don.decoy.0.pwm don.1.txt don.decoy.1.txt
python3 pwm-tester.py acc.0.pwm acc.random.0.pwm acc.1.txt acc.random.1.txt
python3 pwm-tester.py acc.0.pwm acc.decoy.0.pwm acc.1.txt acc.decoy.1.txt
```

You should find something like the following:

- Donor vs. random: 81%
- Donor vs. decoy: 78%
- Acceptor vs. random: 83%
- Acceptor vs. decoy: 78%

Apparently it's easier to discriminate real sites from random than real sites
from decoy. Is this because some of the decoy sites are actually alternative
splice sites? Or is this because random sequence isn't a very good model of a
splice site? There's probably some of the former and a lot of the latter.

## Exons and Introns ##

Even though exons and introns are variable length features, for the purposes of
this exercise, we are going to make them fixed length (for reasons you will see
later). Run the following command lines to sample the exon and intron sequences
and create files of fixed length sequence.

```
python3 exon-intron.py cds.fa.gz 20000 > exons.txt
python3 exon-intron.py introns.fa.gz 20000 > introns.txt
```

Examine the `exons.txt` and `introns.txt` files with `less`. Can you see any
obvious differences by eye?

Once again, we will split these into testing and training sets.

```
python3 splitter.py exons.txt 2 exons
python3 splitter.py introns.txt 2 introns
```

Build a kmer table showing the _differences_ between exons and introns with the
following command:


```
python3 kmer-maker.py exons.0.txt introns.0.txt 4 > exon-vs-intron.4.kmer
```

Examine the `exon-intron.4.kmer` file with `less`. Instead of a file of
probabilities (which was used for PWMs), this is a file of log-odds ratios. A
positive number means the sequence is more likely to occur in exons than
introns. A negative number is the reverse. Sort the file by the second column
to find out which kmer is most indicative of exon and which is most indicative
of intron.

You should find that `TTTT` is the kmer most indicative of introns. But what
about its complement `AAAA`? Exons are apparently GC-rich and also Purine-rich.

Let's see if the model discriminates between real exons and introns in the
testing set.

```
python3 kmer-tester.py exon-vs-intron.4.kmer exons.1.txt introns.1.txt
```

You should see around 88% accuracy.

## Cross-Validation ##

In the experiments above, you trained a model on training data and tested it on
testing data. While you're not allowed to train and test on the same data, you
are allowed to swap positions of testing and training. That is, you can perform
the whole operation twice and take the average of the two performance figures.
This is useful when data is limiting. You can extend this concept to multiple
data splits.

- no cross-validation (what we did)
	- train: set0
	- test: set1
- 2-fold cross-validation (swap training and testing)
	- run 1:
		- train: set0
		- test: set1
	- run 2:
		- train: set1
		- test: set0
- 3-fold cross-validation (train on more data than test)
	- run 1:
		- train: set0 + set1
		- test: set2
	- run 2:
		- train: set0 + set2
		- test: set1
	- run 3:
		- train: set1 + set2
		- test: set0

You can make as many splits as you have sequences. If you have 100 sequences
and split it 100 ways, it's called jacknifing.

## Automation and Experimentation ##

- Can you automate the training and testing of PWMs?
- Can you automate 2-fold cross-validation or higher?
- Can you make these opearations tidy (keep files organized in directories)?
- Can you do the same for kmers?

Questions:

- What is the optimal length of PWMs?
- What is the optimal size for k in exons vs. introns?
- What happens if you test and train on the same data?
- Would a PWM model work for exons and introns?
- Would a kmer model work for splice sites?


## Perceptron ##

Neural networks are popular for many kinds of machine learning tasks. Let's
build and test a neural network to recognize sequence features.

This section needs new software. Install and then activate the "mldemo"
environment using the `mldemo.yml` file provided.

```
module load conda
conda env create -f mldemo.yml
conda activate mldemo
```

The program we will use is called `mlp.py`. It's a little complicated to
explain the code, but the usage is relatively simple.

```
python3 mlp.py
```

You must give the program 2 files, a file of true sequences and a file of fake
sequences. It will therefore work with the files you have already made.

The next arguments are the "shape" of the neural network. For the splice site
experiments that are 10 nt long, the first dimension maps the nucleotides to 4
states with one-hot encoding. If there are 10 nts, there are 40 input states.
The last dimension must be 1. So here's how to run one of the splice site
experiments.

```
python3 mlp.py don.txt don.random.txt 40 1
python3 mlp.py don.txt don.decoy.txt 40 1
python3 mlp.py acc.txt acc.random.txt 40 1
python3 mlp.py acc.txt acc.decoy.txt 40 1
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
layers. In the examples below, there is a middle layer.

```
python3 mlp.py acc.txt acc.random.txt 40 10 1
python3 mlp.py exons.txt introns.txt 200 20 1
```

Adding "hidden" layers between the input and output layers sometimes makes a
neural network perform much better. But not always. "Tuning" a neural network
for optimal perfomance requires modifying the hidden layers as well as a large
number of other "hyper-parameters".

Try tuning your models to see if you can make them perform better.

## Shootout ##

The reason why all of the sequences are fixed length is so you can compare them
to each other easily. It's hard to use a PWM or MLP when you don't know exactly
how long the sequence is.

Make the most accurate model for acceptors, donors, and exon/intron. Which type
of model is best? Which parameters are best?

