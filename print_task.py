# -*- coding: utf-8 -*-
import sys
import os
import re
import yaml
import argparse

def setArgs(parser):
    parser.add_argument('--config', action='store', dest='config_file')
    parser.add_argument('-t', '--task_file', action='store', dest='task_file')

def getPrintTaskOptions(options):
    if options.config_file == None:
        sys.stderr.write('config file is required.\n')
        sys.exit()

    options.task_file = open(options.task_file, 'w') if options.task_file else sys.stdout

    config = yaml.load(open(options.config_file, 'r'))
    options.rawPrefix = config['ExpLocation']['rawPrefix']
    options.sampleTmpDir = config['ExpLocation']['sampleTmpDir'] 
    options.parallelTmpDir = config['ExpLocation']['parallelTmpDir'] 
    options.type = config['ExpSetting']['type']

def printTaskFile(options):
    getPrintTaskOptions(options)

    raw_dir, raw_file_prefix = os.path.dirname(options.rawPrefix), os.path.basename(options.rawPrefix)
    regex = re.compile(r'\d+')

    for fileName in os.listdir(raw_dir):
        if not fileName.startswith(raw_file_prefix):
            continue

        fileID = regex.search(fileName).group(0)
        rawFile = "%s/%s" % (raw_dir, fileName)
        parallelTmpFile = "%s/%s" % (options.parallelTmpDir, fileID)
        sampleTmpFile = "%s/%s" % (options.sampleTmpDir, fileID)

        extract_cmd = "python make_sample.py extract_sample %s --output_file %s --config %s" % (rawFile, parallelTmpFile, options.config_file)
        if options.type == 'REP':
            sort_cmd = "nice -n 19 sort -o %s %s" % (parallelTmpFile, parallelTmpFile)
            sort_cmd = "%s && python ./merge.py %s %s" % (sort_cmd, parallelTmpFile, sampleTmpFile)
        else:
            sort_cmd = "nice -n 19 sort -u -o %s %s" % (sampleTmpFile, parallelTmpFile)
        echo_cmd = "echo %s done" % fileID
        cmd = " && ".join([extract_cmd, sort_cmd, echo_cmd])

        options.task_file.write("%s\n" % cmd)

