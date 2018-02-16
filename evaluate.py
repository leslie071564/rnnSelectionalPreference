# -*- coding: utf-8 -*-
import sys
import argparse
from sqlalchemy import *
from ResultExtractors import knmtResultExtractor, rnnlmResultExtractor

def get_result_db_cursor(db_loc):
    engine = create_engine('sqlite:///%s' % db_loc, echo=False)
    metadata = MetaData(engine)

    result_table = Table('overview', metadata, 
                         Column("source_rep", String()), 
                         Column("arg_list", String()), 
                         Column("pred_list", String()), 
                         Column("output_list", String()), 
                         Column("target_arg", String()), 
                         Column("target_case", String()), 
                         Column("target_pred", String()),
                         Column("raw_sents", String()) )

    result_table.create()
    insert_cursor = result_table.insert()

    return insert_cursor

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--source_file", action="store", dest="source_file")
    parser.add_argument('-t', "--target_file", action="store", dest="target_file")
    parser.add_argument('-o', "--output_file", action="store", dest="output_file")
    parser.add_argument('-r', "--result_db", action="store", dest="result_db")

    parser.add_argument("--rnnlm", action="store_true", dest="rnnlm")
    parser.add_argument("--knmt", action="store_true", dest="knmt")

    parser.add_argument("--top_10_eval", action="store_true", dest="top_10_eval")
    options = parser.parse_args() 

    if options.knmt:
        result_extractor = knmtResultExtractor(options.source_file, options.target_file, options.output_file)

    elif options.rnnlm:
        result_extractor = rnnlmResultExtractor(options.source_file, options.output_file)

    else:
        sys.stderr.write("please specify type of experiment. (knmt/rnnlm)\n")
        sys.exit()

    if options.top_10_eval:
        result_extractor.eval_by_top10()

    else:
        result_db_cursor = get_result_db_cursor(options.result_db)
        row_data = result_extractor.export_result(result_db_cursor)

