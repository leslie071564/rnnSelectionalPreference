# -*- coding: utf-8 -*-
import os
import sys
import yaml
from SampleGenerator import SampleGenerator 

def setArgs(parser):
    parser.add_argument('raw_file', action='store')
    parser.add_argument('-o', '--output_file', action='store', dest='output_file')
    parser.add_argument('--config', action='store', dest='config_file')

def extractSample(options):
    config = yaml.load(open(options.config_file, 'r'))
    exp_settings = config['ExpSetting']

    generator = SampleGenerator(exp_settings)
    generator.printSample(options.raw_file, options.output_file)

