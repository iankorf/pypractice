python3 splices.py introns.fa.gz --limit 20000

python3 splitter.py don.txt 2 don
python3 splitter.py acc.txt 2 acc

python3 pwm-maker.py don.0.txt > don.0.pwm
python3 pwm-maker.py acc.0.txt > acc.0.pwm

python3 random-splices.py 20000 10 --donor > don.random.txt
python3 decoy-splices.py introns.fa.gz 20000 10 --donor > don.decoy.txt
python3 random-splices.py 20000 10 --acceptor > acc.random.txt
python3 decoy-splices.py introns.fa.gz 20000 10 --acceptor > acc.decoy.txt

python3 splitter.py don.random.txt 2 don.random
python3 splitter.py don.decoy.txt 2 don.decoy
python3 splitter.py acc.random.txt 2 acc.random
python3 splitter.py acc.decoy.txt 2 acc.decoy

python3 pwm-maker.py don.random.0.txt > don.random.0.pwm
python3 pwm-maker.py don.decoy.0.txt > don.decoy.0.pwm
python3 pwm-maker.py acc.random.0.txt > acc.random.0.pwm
python3 pwm-maker.py acc.decoy.0.txt > acc.decoy.0.pwm

python3 pwm-tester.py don.0.pwm don.random.0.pwm don.1.txt don.random.1.txt
python3 pwm-tester.py don.0.pwm don.decoy.0.pwm don.1.txt don.decoy.1.txt
python3 pwm-tester.py acc.0.pwm acc.random.0.pwm acc.1.txt acc.random.1.txt
python3 pwm-tester.py acc.0.pwm acc.decoy.0.pwm acc.1.txt acc.decoy.1.txt

python3 exon-intron.py cds.fa.gz 20000 > exons.txt
python3 exon-intron.py introns.fa.gz 20000 > introns.txt

python3 splitter.py exons.txt 2 exons
python3 splitter.py introns.txt 2 introns

python3 kmer-maker.py exons.0.txt introns.0.txt 4 > exon-vs-intron.4.kmer

python3 kmer-tester.py exon-vs-intron.4.kmer exons.1.txt introns.1.txt

python3 mlp.py don.txt don.random.txt 40 1
python3 mlp.py don.txt don.decoy.txt 40 1
python3 mlp.py acc.txt acc.random.txt 40 1
python3 mlp.py acc.txt acc.decoy.txt 40 1

python3 mlp.py exons.txt introns.txt 200 1

python3 mlp.py acc.txt acc.random.txt 40 10 1
python3 mlp.py exons.txt introns.txt 200 20 1