# -*- coding: utf-8 -*-
import sys
import yaml
import argparse

def setArgs(parser):
    parser.add_argument('sampleFile', action='store')
    parser.add_argument('expDir', action='store')
    parser.add_argument('-c', '--config', action='store', default='./train_config.yaml', dest='config_file')

    parser.add_argument('-t', '--test_size', action='store', type=int, default=10000, dest='testSize')
    parser.add_argument('-d', '--dev_size', action='store', type=int, default=10000, dest='devSize')
    parser.add_argument('-e', '--train_size', action='store', type=int, dest='trainSize')

def completeOptions(options):
    options.sampleConfig = options.sampleFile + ".make_sample_config.yaml"

    options.expDataDir = "%s/data" % options.expDir
    options.expTrainDir = "%s/train" % options.expDir
    options.expResultDir = "%s/result" % options.expDir

    # apply default settings
    if options.trainSize == None:
        options.trainSize = 'all'
    
    sample_config = yaml.load(open(options.sampleConfig))
    options.type = sample_config['ExpSetting']['type']

def writeConfig(options):
    completeOptions(options)

    dataLocs = ['sampleFile', 'sampleConfig', 'expDir', 'expDataDir', 'expTrainDir', 'expResultDir']
    dataLocs = dict((arg, getattr(options, arg)) for arg in dataLocs)

    expSettings = ['type', 'testSize', 'devSize', 'trainSize']
    expSettings = dict((arg, getattr(options, arg)) for arg in expSettings)

    allArgs = {'ExpLocation' : dataLocs, 'ExpSetting' : expSettings}
    with open(options.config_file, 'w') as f:
        yaml.dump(allArgs, f, default_flow_style=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    setArgs(parser)
    options = parser.parse_args()

    writeConfig(options)