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

def setArgs(parser):
    parser.add_argument('rawPrefix', action='store')
    parser.add_argument('sampleFile', action='store')
    parser.add_argument('-c', '--config', action='store', default='./make_sample_config.yaml', dest='config_file')
    parser.add_argument('-t', '--tmpPrefix', action='store', dest='tmpPrefix')
    parser.add_argument('-p', '--parallelPrefix', action='store', dest='parallelPrefix')

    parser.add_argument('--type', action='store', default='MT', dest='type', choices=TYPES)
    parser.add_argument('--sampleFormat', action='store', default='targetLast', dest='sampleFormat', choices=FORMATS)
    parser.add_argument('--targetCases', action='store', default='main', dest='targetCases', choices=TARGETCASES)

    parser.add_argument('--removeHiragana', action='store_false', dest='removeHiragana')
    parser.add_argument('--onlySimplePredicate', action='store_false', dest='onlySimplePredicate')
    parser.add_argument('--onlyMultiArg', action='store_false', dest='onlyMultiArg')


def writeConfig(options):
    # apply default settings
    sampleDir, sampleFilePrefix = os.path.dirname(options.sampleFile), os.path.basename(options.sampleFile).split('.')[0]

    if options.parallelPrefix is None:
        options.parallelPrefix = "/data/%s/%s/tmp" %  (getpass.getuser(), sampleFilePrefix)

    if options.tmpPrefix == None:
        options.tmpPrefix = "%s/%s/tmp" % (sampleDir, sampleFilePrefix)

    """
    # mkdir?
    parallelDir = os.path.dirname(options.parallelPrefix)
    tmpDir = os.path.dirname(options.tmpPrefix)
    os.mkdir(parallelDir)
    os.mkdir(tmpDir)
    """

    dataLocs = dict((arg, getattr(options, arg)) for arg in ['rawPrefix', 'sampleFile', 'parallelPrefix', 'tmpPrefix'])

    # experimental settings.
    if options.targetCases == 'main':
        options.targetCases = ['ga', 'wo', 'ni', 'de', 'wa']
    else:
        options.targetCases = EngCases

    options.targetPreds = EngPreds

    expSettings = dict((arg, getattr(options, arg)) for arg in ['type', 'sampleFormat', 'targetCases', 'targetPreds', 'removeHiragana', 'onlySimplePredicate', 'onlyMultiArg'])

    # all args
    allArgs = {'ExpLocation' : dataLocs, 'ExpSetting' : expSettings}
    with open(options.config_file, 'w') as f:
        yaml.dump(allArgs, f, default_flow_style=False)

