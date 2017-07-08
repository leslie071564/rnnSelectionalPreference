# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml
from SampleGenerator import *
from utils import *

def checkExpSettings(config):
    """
    check for conflict in experimental settings.
    (ex: the TargetLast and PlaceHolder option cannot be True together)
    """
    exp_settings = config['ExpSetting']

    if exp_settings['targetLast'] and exp_settings['placeHolder']:
        return False
    elif not exp_settings['targetLast'] and not exp_settings['placeHolder']:
        return False

    if exp_settings['sampleType'] not in ['MT', 'LM', 'REP']:
        return False

    if set(exp_settings['targetCases']) > set(EngCases):
        return False

    if set(exp_settings['targetPreds']) > set(EngPreds):
        return False

    return exp_settings

def print_task_file(config_loc, raw_prefix, output_file):
    output_file = open(output_file, 'w')
    raw_dir = os.path.dirname(raw_prefix)
    regex = re.compile(r'\d+')

    for fileName in os.listdir(raw_dir):
        fileID = regex.search(fileName).group(0)
        cmd = "./preProcess.sh %s %s" % (fileID, config_loc)
        output_file.write("%s\n" % cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--input_file", action="store", dest="input_file")
    parser.add_argument('-o', "--output_file", action="store", dest="output_file")
    parser.add_argument("--config", action="store", dest="config")

    parser.add_argument("--print_task_file", action="store_true", dest="print_task_file")
    parser.add_argument("--merge_file", action="store_true", dest="merged_file")
    options = parser.parse_args()

    config = yaml.load(open(options.config, 'r'))
    config_path = os.path.abspath(options.config)
    exp_settings = checkExpSettings(config)
    if not exp_settings:
        sys.stderr.write('The config file is not properly set. Check again:\n %s\n' % (config_path))
        sys.exit()

    if options.print_task_file:
        rawPrefix = config['ExpLocation']['PreProcess']['RawPrefix']
        print_task_file(config_path, rawPrefix, options.output_file)
        sys.exit()

    sample_type = exp_settings['sampleType']
    if sample_type == 'MT':
        mt = MTSampleGenerator(exp_settings)
        mt.printMTSample(options.input_file, options.output_file)

    elif sample_type == 'LM':
        lm = LMSampleGenerator(exp_settings)
        lm.printLMSample(options.input_file, options.output_file)

    elif sample_type == 'REP':
        rep = RepStrGenerator(exp_settings)
        if options.merged_file:
            rep.mergeRepFile(options.input_file, options.output_file)
        else:
            rep.printRepFile(options.input_file, options.output_file)

