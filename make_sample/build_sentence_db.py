# -*- coding: utf-8 -*-
import sys
from CDB_Writer import CDB_Writer
import argparse
import codecs

def write_event_sid_db(input_file, db_file):
    if db_file.endswith('.keymap'):
        db_file = db_file.split('.keymap')[0]

    DEFAULTLFS = 2.5 * 1024 * 1024 * 1024
    keymap_file = db_file.split('/')[-1] + '.keymap'
    limit_file_size = DEFAULTLFS
    fetch = 10000
    encoding_in = 'utf8'
    encoding_out = 'utf8'

    maker = CDB_Writer(db_file, keymap_file, limit_file_size, fetch, encoding_out)
    with open(input_file, 'r') as f:
        for l in f:
            ev, sids = l.strip().split('###')
            maker.add(ev.decode(encoding_in), sids)

    del maker


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--input_file", action="store", dest="input_file")
    parser.add_argument('-o', "--output_db", action="store", dest="output_db")
    options = parser.parse_args() 

    write_event_sid_db(options.input_file, options.output_db)

