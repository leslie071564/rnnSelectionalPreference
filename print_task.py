# -*- coding: utf-8 -*-
import sys
import os
import re
import yaml
import argparse

def setArgs(parser):
    parser.add_argument('--config', action='store', dest='config_file')
    parser.add_argument('-t', '--task_file', action='store', dest='task_file')
    parser.add_argument('-r', '--rawPrefix', action='store', dest='rawPrefix')

def completeOptions(options):
    if options.config_file == None:
        sys.stderr.write('config file is required.\n')
        sys.exit()

    options.task_file = open(options.task_file, 'w') if options.task_file else sys.stdout

    config = yaml.load(open(options.config_file, 'r'))
    if options.rawPrefix == None:
        options.rawPrefix = config['ExpLocation']['rawPrefix']

    options.tmpPrefix = config['ExpLocation']['tmpPrefix'] 
    options.parallelPrefix = config['ExpLocation']['parallelPrefix'] 

def printTaskFile(options):
    completeOptions(options)

    raw_dir, raw_file_prefix = os.path.dirname(options.rawPrefix), os.path.basename(options.rawPrefix)
    regex = re.compile(r'\d+')

    for fileName in os.listdir(raw_dir):
        if not fileName.startswith(raw_file_prefix):
            continue

        fileID = regex.search(fileName).group(0)
        rawFile = "%s/%s" % (raw_dir, fileName)
        parallelFile = "%s%s" % (options.parallelPrefix, fileID)
        tmpFile = "%s%s" % (options.tmpPrefix, fileID)

        cmd_1 = "python make_sample.py extract_sample %s --output_file %s --config %s" % (rawFile, parallelFile, options.config_file)
        cmd_2 = "nice -n 19 sort -u -o %s %s" % (tmpFile, parallelFile)
        cmd_3 = "echo %s done" % fileID
        cmd = "%s && %s && %s" % (cmd_1, cmd_2, cmd_3)

        options.task_file.write("%s\n" % cmd)

