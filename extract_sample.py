# -*- coding: utf-8 -*-
import os
import sys
import yaml
from SampleGenerator import MTSampleGenerator, LMSampleGenerator

def setArgs(parser):
    parser.add_argument('raw_file', action='store')
    parser.add_argument('-o', '--output_file', action='store', dest='output_file')
    parser.add_argument('--config', action='store', dest='config_file')

def extractSample(options):
    config = yaml.load(open(options.config_file, 'r'))
    exp_settings = config['ExpSetting']
    sample_type = config['ExpSetting']['type']

    if sample_type == 'MT':
        mt = MTSampleGenerator(exp_settings)
        mt.printMTSample(options.raw_file, options.output_file)

    elif sample_type == 'LM':
        lm = LMSampleGenerator(exp_settings)
        lm.printLMSample(options.raw_file, options.output_file)

