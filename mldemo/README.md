Sequence Patterns Machine Learning Demo
=======================================

In this unit, you will explore several ways to get a computer to recognize the
differences between various kinds of genomic sequence. In other words, we're
going to teach a computer how to "read the book of life". In genomic sequence,
there tend to be 2 kinds of "features"

1. Fixed length features, like splice sites
2. Variable length features, like exons and introns

To model fixed length features, specifically splice donor and splice acceptor
sites, we will use a Position Weight Matrices. For variable length features, we
will use kmers.

Both of these constructs should be familiar to you. When we built the IMEter,
that was a kmer model. When we found the motifs present in high scoring introns
with MEME, those motifs were position weight matrices.

To create these models, we need exon and intron sequences. These are in the
directory as `cds.fa.gz` (coding sequence) and `introns.fa.gz`.

## Splice Sites ##

### True Sites

Extract the donor and acceptor sites as follows:

```
python3 splices.py introns.fa.gz
```

This results in 2 files: `acc.txt` and `don.txt`. Use `less` to examine the
files and you will find the sequences are all 10 nt long. The file names and 10
are default parameters of the program, but these can be overridden with
commandline options. When you write your own programs, do not hard-code paths
or parameters unless you also provide a way to override them, like this program
does.

How many sequences are there? (hint: use `wc`). Did you notice this isn't the
same number as the input sequences? Can you figure out why that is?

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
But how well does the model actually work? To start answering this question, we
need some fake/decoy sites. We need to be able to ask "does some new
observation look more like a real site or a fake site?" Where do we get fake
sites?

We often compare _things_ to a random model, so it seems like generating random
sequences is an okay place to start. But random sequences lack biological
context. Another source of data _should_ be biological. What sequences are
definitely not splice sites? That turns out to be a difficult question.
Alternative splicing exists, and maybe our data would look different if we
sequenced a different tissue. Here are some ideas for where fake sites might
come from.

- Intergenic sequence
	- but how do we _know_ there is no gene there?
- The middle of exons
	- but how do we know there isn't any alternative splicing?
	- and exons have different compositions compared to introns
- Other GTs and AGs in introns
	- but alternative splicing exists...
- The opposite strand
	- but is the composition on the opposite strand the same?


fake data maker

### Training & Testing


something for sub-sampling to make test/train from everything



## Markov Models ##


## Weight Array Matrix ##

## Perceptron ##

## Multi-layer Perceptron ##



Splice sites
Coding
Intron
