# -*- coding: utf-8 -*-
import os
import sys
import yaml
import getpass
import argparse
from utils import EngCases, EngPreds

TYPES = ['MT', 'LM', 'REP']
FORMATS = ['targetLast', 'placeHolder']
TARGETCASES = ['main', 'all']
INTRANS_LOC = "/mnt/hinoki/huang/rnnSelectionalPreference/intrans.txt"

def setArgs(parser):
    parser.add_argument('rawPrefix', action='store')
    parser.add_argument('sampleDir', action='store')
    parser.add_argument('--config', action='store', default='./make_sample_config.yaml', dest='config_file')

    parser.add_argument('-p', '--parallelTmpDir', action='store', default='/data/$USER/tmp_rnnsp', dest='parallelTmpDir')
    parser.add_argument('-t', '--sampleTmpDir', action='store', default='$sampleDir/tmp', dest='sampleTmpDir')
    parser.add_argument("--intrans_list_file", action='store', default=INTRANS_LOC, dest='intrans_list_file')

    parser.add_argument('--type', action='store', default='MT', dest='type', choices=TYPES)
    parser.add_argument('--sampleFormat', action='store', default='targetLast', dest='sampleFormat', choices=FORMATS)
    parser.add_argument('--targetCases', action='store', default='main', dest='targetCases', choices=TARGETCASES)

    parser.add_argument('--removeHiragana', action='store_true', dest='removeHiragana')
    parser.add_argument('--includePostfix', action='store_true', dest='includePostfix')
    parser.add_argument('--splitPostfix', action='store_true', dest='splitPostfix')
    parser.add_argument('--includeTense', action='store_true', dest='includeTense')
    parser.add_argument('--onlyMultiArg', action='store_true', dest='onlyMultiArg')
    parser.add_argument('--onlyMultiPA', action='store_true', dest='onlyMultiPA')
    parser.add_argument('--extractIntrans', action='store_true', dest='extractIntrans')


def get_write_config_options(options):
    # apply default settings
    options.parallelTmpDir = options.parallelTmpDir.replace('$USER', getpass.getuser())
    options.sampleTmpDir = options.sampleTmpDir.replace('$sampleDir', options.sampleDir)

    # experimental settings.
    if options.targetCases == 'main':
        options.targetCases = ['ga', 'wo', 'ni', 'de', 'wa']
    else:
        options.targetCases = EngCases
    options.targetPreds = EngPreds

    return options


def writeConfig(options):
    options = get_write_config_options(options)

    # build config_file hierarchy.
    dataLocs = dict((arg, getattr(options, arg)) for arg in ['rawPrefix', 'sampleDir', 'parallelTmpDir', 'sampleTmpDir'])
    expSettings = dict((arg, getattr(options, arg)) for arg in ['type', 'sampleFormat', 'targetCases', 'targetPreds', 'removeHiragana', 'includePostfix', 'splitPostfix', 'includeTense', 'onlyMultiArg', 'onlyMultiPA', 'extractIntrans', 'intrans_list_file'])

    allArgs = {'ExpLocation' : dataLocs, 'ExpSetting' : expSettings}

    # write config_file
    with open(options.config_file, 'w') as f:
        yaml.dump(allArgs, f, default_flow_style=False)

