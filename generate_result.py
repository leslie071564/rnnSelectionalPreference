# -*- coding: utf-8 -*-
import sys
import argparse
import sqlite3
from collections import defaultdict
from itertools import izip
from getSentence import getEventSentences
from utils import getPAstr, SQLtable
pa2sid = "/windroot/huang/neuralCF_data/sidSearch/cdbs/pa2sid.cdb"


class knmtFilesProcessor(object):
    def __init__(self, sourceFile, targetFile, outputFile):
        self.saveResult(sourceFile, targetFile, outputFile)

    def saveResult(self, sourceFile, targetFile, outputFile):
        self._processTestFile(sourceFile, targetFile)
        self._processOutputFile(outputFile)

    def _processTestFile(self, sourceFile, targetFile):
        ret = getEventSentences(pa2sid)
        self.testData = {}
        for index, (src, tgt) in enumerate(izip(open(sourceFile, 'rb'), open(targetFile, 'rb'))):
            src, tgt = src.rstrip().encode('utf-8'), tgt.rstrip().encode('utf-8')
            targetArg = tgt
            args, pred, targetCase = src.split()[:-2], src.split()[-2], src.split()[-1]

            source = "%s ___ %s %s" % (" ".join(args), targetCase, pred)

            iArgs = iter(args)
            allArgs = [list(x) for x in zip(iArgs, iArgs)] + [[targetArg, targetCase]]
            paStr = getPAstr(allArgs, pred)
            sents = ret.event_to_sentence(paStr).values() 

            self.testData[index] = {'src' : source, 'tgtArg': targetArg, 'tgtCase': targetCase, 'sents': sents}
            sys.stderr.write("processing test %s\n" % index)

    def _processOutputFile(self, outputFile):
        self.bestN = defaultdict(list)
        for line in open(outputFile, 'rb').readlines():
            index, out = line.rstrip().split(' ||| ')
            index = int(index)
            if "UNK" in out:
                out = "UNK"

            self.bestN[index].append(out)

        self.bestN = dict(self.bestN)

    def writeResultDB(self, db_loc):
        conn = sqlite3.connect(db_loc)
        c = conn.cursor()
        cols = ["source", "target_case", "target_arg", "output", "sents"]
        table_name = "result"
        self.resultDB = SQLtable(c, cols, table_name)

        for index, testInstance in self.testData.iteritems():
            result = [str(index)]
            result.append(testInstance["src"])
            result.append(testInstance['tgtCase'])
            result.append(testInstance['tgtArg'])
            result.append("|".join(self.bestN[index]))
            result.append("|".join(testInstance['sents']))
            self.resultDB.set_row(result)

        conn.commit()
        conn.close()


class rnnlmFilesProcessor(object):
    def __init__(self, testFile, outputFile):
        self.saveResult(testFile, outputFile)

    def saveResult(self, testFile, outputFile):
        self._processTestFile(testFile)
        self._processOutputFile(outputFile)

    def _processTestFile(self, testFile):
        ret = getEventSentences(pa2sid)
        self.testData = {}
        for index, src in enumerate(open(testFile, 'rb').readlines()):
            src = src.rstrip().encode('utf-8')
            pred, args = src.split()[0], src.split()[1:]
            targetCase, targetArg = args[-2], args[-1]

            source = "%s ___ %s %s" % (" ".join(args[:-2]), targetCase, pred)

            iArgs = iter(args[::-1])
            allArgs = [list(x) for x in zip(iArgs, iArgs)]
            paStr = getPAstr(allArgs, pred)
            sents = ret.event_to_sentence(paStr).values() 

            self.testData[index] = {'src' : source, 'tgtArg': targetArg, 'tgtCase': targetCase, 'sents': sents}
            sys.stderr.write("processing test %s\n" % index)

    def _processOutputFile(self, outputFile):
        self.bestN = defaultdict(list)
        index = 0
        for line in open(outputFile, 'rb').readlines():
            line = line.rstrip()
            if line[0] != "\t":
                index += 1
                continue
            out, _ = line.lstrip().split()
            self.bestN[index].append(out)

    def writeResultDB(self, db_loc):
        conn = sqlite3.connect(db_loc)
        c = conn.cursor()
        cols = ["source", "target_case", "target_arg", "output", "sents"]
        table_name = "result"
        self.resultDB = SQLtable(c, cols, table_name)

        for index, testInstance in self.testData.iteritems():
            if index not in self.bestN.keys():
                sys.stderr.write("%s no output (OOV problem).\n" % index)
                continue
            result = [str(index)]
            result.append(testInstance["src"])
            result.append(testInstance['tgtCase'])
            result.append(testInstance['tgtArg'])
            result.append("|".join(self.bestN[index]))
            result.append("|".join(testInstance['sents']))
            self.resultDB.set_row(result)

        conn.commit()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--source_file", action="store", dest="source_file")
    parser.add_argument('-t', "--target_file", action="store", dest="target_file")
    parser.add_argument('-o', "--output_file", action="store", dest="output_file")
    parser.add_argument('-r', "--result_db", action="store", dest="result_db")

    parser.add_argument("--rnnlm", action="store_true", dest="rnnlm")
    parser.add_argument("--knmt", action="store_true", dest="knmt")
    options = parser.parse_args() 

    if options.knmt:
        x = knmtFilesProcessor(options.source_file, options.target_file, options.output_file)
        x.writeResultDB(options.result_db)

    elif options.rnnlm:
        x = rnnlmFilesProcessor(options.source_file, options.output_file)
        x.writeResultDB(options.result_db)

