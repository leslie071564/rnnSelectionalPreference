# -*- coding: utf-8 -*-
import sys
import json
import h5py
import pickle
import argparse
import numpy as np

def getScoreArray(score_file, index):
    data = h5py.File(score_file, 'r')
    return data['scores_%s' % index][0]

def convertCandidate(candidate_list, voc_file):
    data = json.load(open(voc_file, 'r'))
    tgt_list = data['indexer_tgt']['indexer']['voc_lst']
    tgt_dict = {w : index for index, w in enumerate(tgt_list)}

    candidate_indexes = []
    for w in candidate_list:
        w = w.decode('utf-8')
        if w not in tgt_list:
            candidate_indexes.append(None)
        else:
            candidate_indexes.append(tgt_dict[w])
    return candidate_indexes

def getCandidateScores(candidate_indexes, scores):
    candi_scores = []
    for index in candidate_indexes:
        if index == None:
            candi_scores.append(0)
        else:
            candi_scores.append(scores[index])
    return np.array(candi_scores)

def export(conf):
    output_data = {}
    for index, line in enumerate(open(conf.input_file).readlines()):
        sid, src, candidates = line.rstrip().split("###")
        candidate_list = candidates.split('|')

        scores = getScoreArray(conf.score_file, index)
        candidate_indexes = convertCandidate(candidate_list, conf.voc_file)
        candidate_scores = getCandidateScores(candidate_indexes, scores)

        output_data[sid] = candidate_scores

        if conf.debug:
            print "# sid: %s %s" % (sid, src)
            for i, w in enumerate(candidate_list):
                print "\t%s: %.5f" % (w, candidate_scores[i])

    # save to output_file
    output_file = open(conf.output_file, 'w')
    pickle.dump(output_data, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--score_file", action="store", dest="score_file")
    parser.add_argument('-i', "--input_file", action="store", dest="input_file")
    parser.add_argument('-o', "--output_file", action="store", dest="output_file")
    parser.add_argument('-v', "--voc_file", action="store", dest="voc_file")

    parser.add_argument("--debug", action="store_true", dest="debug")
    options = parser.parse_args() 

    export(options)

