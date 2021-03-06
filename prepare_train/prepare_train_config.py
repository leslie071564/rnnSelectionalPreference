# -*- coding: utf-8 -*-
import os
import sys
import yaml
import argparse

def setArgs(parser):
    parser.add_argument('sampleFile', action='store')
    parser.add_argument('expDir', action='store')

    parser.add_argument('--config_file', action='store', dest="config_file")
    parser.add_argument('--training_graph', action='store', dest='trainingGraph')
    parser.add_argument('--result_db', action='store', dest='resultDB')

    parser.add_argument('--test_size', action='store', type=int, default=10000, dest='testSize')
    parser.add_argument('--dev_size', action='store', type=int, default=10000, dest='devSize')
    parser.add_argument('--train_size', action='store', type=int, default=100000000, dest='trainSize')

    parser.add_argument('--src_voc_size', action='store', type=int, default=32000, dest='srcVoc')
    parser.add_argument('--tgt_voc_size', action='store', type=int, default=32000, dest='tgtVoc')

    parser.add_argument('--filter_unk', action='store_true', dest='UNKfilter')

def completeOptions(options):
    exp_name = os.path.basename(options.expDir)
    if options.trainingGraph == None:
        options.trainingGraph = "/home/huang/public_html/rnnSelectionalPreference/knmt/graph/%s.html" % (exp_name)
    if options.resultDB == None:
        options.resultDB = "/home/huang/public_html/rnnSelectionalPreference/knmt/result_dbs/%s.sqlite" % (exp_name)

    if options.config_file == None:
        options.config_file = "%s/train_config.yaml" % options.expDir

    options.sampleConfig = "%s/make_sample_config.yaml" % os.path.dirname(options.sampleFile)

    options.expDataDir = "%s/data" % options.expDir
    options.expTrainDir = "%s/train" % options.expDir
    options.expResultDir = "%s/result" % options.expDir

    sample_config = yaml.load(open(options.sampleConfig))
    options.type = sample_config['ExpSetting']['type']

def writeConfig(options):
    completeOptions(options)

    dataLocs = ['sampleFile', 'sampleConfig', 'expDir', 'expDataDir', 'expTrainDir', 'expResultDir', 'trainingGraph', 'resultDB']
    dataLocs = dict((arg, getattr(options, arg)) for arg in dataLocs)

    expSettings = ['type', 'testSize', 'devSize', 'trainSize', 'srcVoc', 'tgtVoc', 'UNKfilter']
    expSettings = dict((arg, getattr(options, arg)) for arg in expSettings)

    allArgs = {'ExpLocation' : dataLocs, 'ExpSetting' : expSettings}
    with open(options.config_file, 'w') as f:
        yaml.dump(allArgs, f, default_flow_style=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    setArgs(parser)
    options = parser.parse_args()

    writeConfig(options)
