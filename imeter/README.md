IMEter
======

Intron-mediated enhancement is the general phenomenon that introns improve gene
expression. The IMEter is a program that predicts how much an intron will
increase expression. In this project, you will rebuild that tool and parts of
the original papers.

## Papers ##

These 2 papers are an easy read.

- tpc2000543.pdf
- 978-1-60327-563-7_14.pdf

## Proximal vs. Distal Introns ##

The IMEter is based on the simple concept that introns near the start of a gene
are different from introns near the end of a gene. Your first task is to create
datasets of proximal and distal introns.

The `extract-introns.py` program extracts intron sequences from the FASTA and
GFF files provided by TAIR (The Arabidopsis Information Resource). Try running
the program to see its usage statement.

```
python3 extract-introns.py
```

This results in the following error:

```
Traceback (most recent call last):
  File "something...pypractice/imeter/extract-introns.py", line 4, in <module>
    import korflab
ModuleNotFoundError: No module named 'korflab'
```

This error tells you that python can't find a "module" it needs. Some python
modules (also called libraries) are not part of a standard distribution and you
will need to tell python how to find them. There are several ways to do this.
We will do the simplest one, which is to move the file (or rather a link) to
the directory with the program you want to run.

First, go to your home directory and clone the KorfLab/setup repo.

```
cd
git clone https://github.com/KorfLab/setup
```

Then go back to your pypractice/imeter directory and soft link the file. Note
the dot at the end of the second line below.

```
cd pypractice/imeter
ln -s ~/setup/lib/korflab.py .
ls -l
```

You now have a shortcut to `korflab.py` in your `pypractice/imeter` directory.
Python can now find the library easily and `extract-introns.py` will work.

```
python3 extract-introns.py TAIR9_chr_all.fas.gz Araport11.gff.gz > introns.fa
```

How _exactly_ does this program work? Go ahead and view any of the *.py files.
They are all just python.

Examine the output file `introns.fa` with `less`. An example is show below.

```
>AT1G01010.1-1|284-365|Chr1:3914-3995 FORWARD LENGTH=82
GTAAGTTCCGAATTTTCTGAATTTCATTTGCAAGTAATCGATTTAGGTTTTTGATTTTAGGGTTTTTTTTTGTTTTGAAC
AG
```

This is the first intron from the gene `AT1G01010.1`. The coordinates relative
to the transcript are 284-365. It's genomic coordinates are 3914-3995 on
Chromosome 1. The gene is on the forward (plus) strand, and the sequence is 82
nt long. As expected, the intron begins with `GT` and ends with `AG`.

Recall that introns near the beginning of a gene are supposedly different from
those near the end. To determine if this is true, you need to separate introns
based on their position.

Examine the `isplitter.py` program to see how this can be done. The program
reads through a FASTA file using the `korflab.readfasta()` function. It gets
the starting position of each intron (e.g. 284 above). If the starting position
is less than some threshold, it prints out the sequence in FASTA format. Let's
try it out.

```
python3 isplitter.py introns.fa 400 > prox400.fa
```

To get the introns on the other side of the threshold, use the `--high` option.

```
python3 isplitter.py introns.fa 400 --high > dist400.fa
```


## Comparing Compositions ##

You now have files of introns from proximal and distal introns. Are they
different from each other? One way to find out is to compare the frequencies of
nucleotides. There are many ways to do this in python. You can write your own
or use `kmercount.py`.

```
python3 kmercount.py prox400.fa 1
python3 kmercount.py dist400.fa 1
```

It's a little hard to compare these outputs because the files aren't the same
size. So pass the `--prob` option to report probabilities.

```
python3 kmercount.py prox400.fa 1 --prob
python3 kmercount.py dist400.fa 1 --prob
```

They are similar, but not exactly the same. Biological signals are often more
like "words" than letters. So let's examine the differences using a larger size
of kmer, such as 5. The problem is that there are 1024 5-mers, so trying to
examine that by eye is going to be difficult. Let's save the results to files
and compare them with a program.

```
python3 kmercount.py prox400.fa 5 --prob > kmers-prox-400-5
python3 kmercount.py dist400.fa 5 --prob > kmers-dist-400-5
python3 kmercompare.py kmers-prox-400-5 kmers-dist-400-5
```

So there's a difference by some sort of measurement, but is the difference
biologically or statistically significant?

## Meaningful Comparisons ##

To figure out if proximal and distal introns are different from each other, we
need some way of measuring what is expected. One way to do this is to split
each set of introns into 2 parts. Then compare the parts to each other. Are
proximal introns similar to other proximal introns? Are distal introns similar
to distal introns? Are they different from each other?

Use the `fasplitter.py` program to randomly split a fasta file into 2 files.

```
python3 fasplitter.py prox400.fa p400a.fa p400b.fa
python3 fasplitter.py dist400.fa d400a.fa d400b.fa
```

Next, make the kmer probabilities of each.

```
python3 kmercount.py --prob p400a.fa 5 > p400a.k5
python3 kmercount.py --prob p400b.fa 5 > p400b.k5
python3 kmercount.py --prob d400a.fa 5 > d400a.k5
python3 kmercount.py --prob d400b.fa 5 > d400b.k5
```

First, let's compare proximal to proximal and distal to distal. This sets up
our expectations for comparing between groups.

```
python3 kmercompare.py p400a.k5 p400b.k5
python3 kmercompare.py d400a.k5 d400b.k5
```

Next, let's compare the proximals to distals.

```
python3 kmercompare.py p400a.k5 d400a.k5
python3 kmercompare.py p400a.k5 d400b.k5
python3 kmercompare.py p400b.k5 d400a.k5
python3 kmercompare.py p400b.k5 d400b.k5
```

Clearly, there is a difference between proximal and distal introns. The "words"
are spoken with different frequencies.

## Shuffling ##

As we saw with sequence alignment, shuffling is often a good way of seeing what
is expected at random. The `fascramble.py` program rearranges the letters in a
FASTA file randomly.

- Make scrambled versions of p400a.fa, p400b.fa, d400a.fa, d400b.fa
- Make kmer probabilities of each
- Compare kmer frequencies of scrambled sequences
	- proximal to proximal
	- distal to distal
	- proximal to distal

What do you find?

## IMEter ##

The file `db_IME_Rose_WT_introns.fa.gz` has experimentally validated introns.
The first FASTA entry looks like this:

```
>dbIMEintron1 TRP1_i1_WT x4.3 AT5G17990.1
GTAAAGCCTCGATTTTTGGGTTTAGGTGTCTGCTTATTAGAGTAAAAACACATCCTTTGA
AATTGTTTGTGGTCATTTGATTGTGCTCTTGATCCATTGAATTGCTGCAG
```

The sequence corresponds to the first intron of the TRP1 gene. This is also
known as AT5G17990.1. It has been observed to increase gene expression by 4.3x
when used in a reporter construct.

The IMEter is an algorithm that predits how much an intron boosts gene
expression by examining its kmer composition compared to proximal and distal
introns. It's simply a sum of log-odds probabilities. Given the sequence above
and and a kmer size of 5, it does the following:

- score starts at 0
- score += log2(prox[GTAAA] / dist[GTAAA])
- score += log2(prox[TAAAG] / dist[TAAAG])
- score += log2(prox[AAAGC] / dist[AAAGC])
- score += log2(prox[AAGCC] / dist[AAGCC])
- score += log2(prox[AGCCT] / dist[AGCCT])
- etc

(In truth, the IMEter skips the first 5 and last 10 bases because these are the
splice donor and acceptor sites whose sequences are generally conserved).

Write a program that reads `db_IME_Rose_WT_introns.fa.gz` and reports the
IMEter score and expression value. Your values should look similar to those
below (but not identical because we may have split the sequences differently).

```
7.528669068478741	4.3
97.1537248754191	12.5
-8.236062631231334	1.4
55.30217039540287	12.3
-25.41482587000839	2.2
-32.91703410856818	1.1
5.3221907782518425	4.0
26.2791486904357	7.2
-16.304565627380384	1.8
-2.281137440101106	0.6
-18.487172420278704	1.2
94.85801630324532	10.2
88.76394478264871	4.1
14.949860798868386	4.9
1.4647402986823728	5.7
```

Make a scatter plot and report the Pearson correlation.


## Figure 3A ##

If you look at Figure 3A from the tpc2000543.pdf paper, you will see the "IME
motif". In subsequent studies, this has been shown to be sufficient to increase
expression. Let's try to find that motif and maybe others using meme.

First, find the highest scoring introns in the genome (e.g. top 100) and put
them into a FASTA file. It's up to you to write that software. Then run
meme to find motifs.

Assuming you have such a file and have `meme` installed, try the following
command (note that meme has many options, some of which will give different
results).


```
meme -dna -minw 5 -maxw 10 -mod zoops -nmotifs 5 top100.fa
```

The output report is `meme_out/meme.html`.


## Figure 14.3 ##

Everything that was done so far was done with a proximal-distal split at 400 nt
and a kmer size of 5. Is this optimal? Maybe it would work better at smaller or
larger sizes of k. Maybe 400 isn't the right split. How would you figure this
out? The answer is to automate everything. It looks a bit like this:

```
for k in range(1, 11):
	for split in range(100, 1100, 100):
		do stuff...
```

This is how Figure 14.3 was made in the 978-1-60327-563-7_14.pdf paper. Can you
automate it?

