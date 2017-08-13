# -*- coding: utf-8 -*-
import sys
import argparse
import sqlite3
from utils import SQLtable 

def writeResultDB(result_file, db_loc):
    conn = sqlite3.connect(db_loc)
    c = conn.cursor()
    cols = ["source", "arg_num", "target_case", "target_arg", "output", "cf_id", "eval_target", "eval_cf", "sents"]
    table_name = "result"
    resultDB = SQLtable(c, cols, table_name)

    for index, line in enumerate(open(result_file, 'rb').readlines()):
        data = line.rstrip().split("###")
        if len(data) != 9:
            sys.stderr.write("error: %s" % line)
        resultDB.set_row([str(index)] + data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', "--result_file", action="store", dest="result_file")
    parser.add_argument('-d', "--result_db", action="store", dest="result_db")
    options = parser.parse_args() 

    writeResultDB(options.result_file, options.result_db)
