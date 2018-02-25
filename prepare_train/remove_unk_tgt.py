# -*- coding: utf-8 -*-
import sys

if __name__ == "__main__":
    data_dir = sys.argv[1]
    tgt_frequent_file = "%s/tgt_frequent.txt" % data_dir
    training_sample_file = "%s/all.txt" % data_dir

    freq_tgts = [line.split()[0] for line in open(tgt_frequent_file).readlines()]
    
    for line in open(training_sample_file, 'rb'):
        line = line.rstrip()
        tgt = line.split('###')[-1]
        if tgt in freq_tgts:
            print line

