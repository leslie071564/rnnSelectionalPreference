# -*- coding: utf-8 -*-
import os
import sys
import yaml
from argparse import Namespace
from SampleGenerator import SampleGenerator 
from utils import cases, preds

def setArgs(parser):
    parser.add_argument('raw_file', action='store')
    parser.add_argument('-o', '--output_file', action='store', dest='output_file')
    parser.add_argument('--config', action='store', dest='config_file')

def getExtractConfig(config_file):
    extract_config = Namespace()
    config = yaml.load(open(config_file, 'r'))
    exp_settings = config['ExpSetting']

    for opt in ['type', 'removeHiragana', 'includePostfix', 'splitPostfix', 'includeTense', 'onlyMultiArg']:
        setattr(extract_config, opt, exp_settings[opt])

    if exp_settings['sampleFormat'] == 'targetLast':
        extract_config.targetLast, extract_config.placeHolder = True, False
    else:
        extract_config.targetLast, extract_config.placeHolder = False, True

    extract_config.targetCases = map(lambda x: cases[x], exp_settings['targetCases'])
    extract_config.targetPreds = map(lambda x: preds[x], exp_settings['targetPreds'])

    return extract_config

def extractSample(options):
    exp_settings = getExtractConfig(options.config_file)

    generator = SampleGenerator(exp_settings)
    generator.printSample(options.raw_file, options.output_file)

