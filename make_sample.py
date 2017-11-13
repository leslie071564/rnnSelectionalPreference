# -*- coding: utf-8 -*-
import sys
import argparse

import make_sample_config as print_config
import print_task
import extract_sample

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subtask')

    # generate config file.
    config_parser = subparsers.add_parser('print_config')
    print_config.setArgs(config_parser)

    # generate task file
    task_parser = subparsers.add_parser('print_task')
    print_task.setArgs(task_parser)

    # generate sample file
    sample_parser = subparsers.add_parser('extract_sample')
    extract_sample.setArgs(sample_parser)

    options = parser.parse_args()

    if options.subtask == 'print_config':
        print_config.writeConfig(options)

    elif options.subtask == 'print_task':
        print_task.printTaskFile(options)

    elif options.subtask == 'extract_sample':
        extract_sample.extractSample(options)


if __name__ == "__main__":
    main()
