pypractice
==========

Practice programming problems to improve your Python

## FizzBuzz ##

Make a program that writes out the numbers from 1 to 100. If the number is divisible by 3, write Fizz instead. If the number is divisible by 5, write Buzz instead. If the number is divisible by both 3 and 5, write FizzBuzz instead.

## tm() ##

Write a function that returns the melting temperature of an oligo. Assume the
input is a string.

- For oligos <= 13 nt, Tm = (A+T)*2 + (G+C)*4
- For longer oligos, Tm = 64.9 + 41*(G+C -16.4) / (A+T+G+C)

## is_prime() ##

Write a function that returns `True` if a number is prime and `False`
otherwise.

## factorial() ##

Write a function that returns the factorial of a number.

## Euler ##

Now that you have a factorial function (which is also available in the math
library), write a program that estimates e (2.718218...) using the infinite
series where e equals sum 1 / n!. Stop the program after some number of
iterations. For bonus points, stop when the precision is better that some
threshold.

## Pi ##

Make a program that estimates Pi by "throwing darts". Given random points `x`
and `y` from 0 to 1, the ratio of the number of points inside an arc of radius
1 to the total points is Pi / 4.

For this problem, you will need `random.random()`.

## Nilakantha ##

Write a program that estimates Pi (3.14159...) using the Nilakantha series.
Stop after some number of iterations or some level of precision.

Pi = 3 + 4/(2x3x4) - 4/(4x5x6) + 4/(6x7x8) - 4/(8x9x10) ...


## Phred ##

Write functions that convert PHRED quality values to ASCII symbols and back.
You will need to use the `ord()` and `chr()` functions.

https://en.wikipedia.org/wiki/FASTQ_format

- The PHRED score of 30 is 1 error in 10**3.0
- PHRED 40 is 1 error in 10**4.0
- The letter `A` has an ASCII value of 65
- The letter `A` corresponds to PHRED 32 (ASCII - 33 to get to PHRED)

## FASTA Stats ##

Write a program that reads FASTA files and reports the following statistics:

- Number of sequences
- Minimum sequence length
- Maximum sequence length
- Average length
- Median length
- N50 length

For bonus points, also report the counts and probabilities of each letter.
You are not allowed to `import statistics` or the equivalent.

## Shotgun ##

Simulate random shotgun sequencing of a genome. Given a genome of size X, read
lengths of size Y, and read counts of number Z, write a program that reports
the fraction of a genome that has not been hit.

## IMEter ##

Rebuild the IMEter. See the `imeter` subdirectory.

## Machine Learning ##

Write some programs that learn what biological patterns look like. See the
`mldemo` subdirectory.
