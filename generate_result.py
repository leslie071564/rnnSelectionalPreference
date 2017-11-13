# -*- coding: utf-8 -*-
import os
import sys
import argparse
from collections import defaultdict
from itertools import izip


class knmtResultExtractor(object):
    def __init__(self, sourceFile, targetFile, outputFile):
        self.saveResult(sourceFile, targetFile, outputFile)

    def saveResult(self, sourceFile, targetFile, outputFile):
        self._processTestFile(sourceFile, targetFile)
        self._processOutputFile(outputFile)

    def _processTestFile(self, sourceFile, targetFile):
        self.testData = {}
        for index, (src, tgt) in enumerate(izip(open(sourceFile, 'rb'), open(targetFile, 'rb'))):
            src, tgt = src.rstrip(), tgt.rstrip()

            targetArg = tgt
            givenArgs, pred, targetCase = src.split()[:-2], src.split()[-2], src.split()[-1]

            self.testData[index] = {'pred': pred, 'givenArgs': givenArgs, 'tgtCase': targetCase, 'tgtArg': targetArg}
            sys.stderr.write("processing test %s\n" % index)

    def _processOutputFile(self, outputFile):
        self.bestN = defaultdict(list)
        for line in open(outputFile, 'rb').readlines():
            index, out = line.rstrip().split(' ||| ')
            if "UNK" in out:
                out = "UNK"

            self.bestN[int(index)].append(out)

        self.bestN = dict(self.bestN)

    def writeTask(self, tmp_folder, file_loc='./generate_result.task'):
        f = open(file_loc, 'wb')

        for index, testInstance in self.testData.iteritems():
            result = []
            result.append(testInstance["pred"])
            result.append(self._formatArgs(testInstance["givenArgs"]))
            result.append(testInstance['tgtCase'])
            result.append(testInstance['tgtArg'])
            if index not in self.bestN.keys():
                result.append('null')
            else:
                result.append('|'.join(self.bestN[index]))

            output_dir = "%s/%s" % (tmp_folder, index/100)
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
            output_file = "%s/%s.txt" % (output_dir, index)

            cmd = 'python evaluate.py -r "%s" > %s' % (' '.join(result), output_file)
            f.write(cmd + '\n')

        f.close()

    def _formatArgs(self, args):
        iArgs = iter(args)
        argList = ["%s=%s" % (case, arg) for arg, case in zip(iArgs, iArgs)]
        return "|".join(argList)

class rnnlmResultExtractor(object):
    def __init__(self, testFile, outputFile):
        self.saveResult(testFile, outputFile)

    def saveResult(self, testFile, outputFile):
        self._processTestFile(testFile)
        self._processOutputFile(outputFile)

    def _processTestFile(self, testFile):
        self.testData = {}
        for index, src in enumerate(open(testFile, 'rb').readlines()):
            src = src.rstrip()
            pred, args = src.split()[0], src.split()[1:]
            givenArgs, targetCase, targetArg = args[:-2], args[-2], args[-1]

            self.testData[index] = {'pred' : pred, 'givenArgs': givenArgs, 'tgtCase' : targetCase, 'tgtArg': targetArg}
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

    def writeTask(self, tmp_folder, file_loc='./generate_result.task'):
        f = open(file_loc, 'wb')

        for index, testInstance in self.testData.iteritems():
            result = []
            result.append(testInstance["pred"])
            result.append(self._formatArgs(testInstance["givenArgs"]))
            result.append(testInstance['tgtCase'])
            result.append(testInstance['tgtArg'])
            if index not in self.bestN.keys():
                result.append('null')
            else:
                result.append('|'.join(self.bestN[index]))

            output_dir = "%s/%s" % (tmp_folder, index/100)
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)
            output_file = "%s/%s.txt" % (output_dir, index)

            cmd = 'python evaluate.py -r "%s" > %s' % (' '.join(result), output_file)
            f.write(cmd + '\n')

        f.close()

    def _formatArgs(self, args):
        iArgs = iter(args)
        argList = ["%s=%s" % (case, arg) for case, arg in zip(iArgs, iArgs)]
        return "|".join(argList)


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
        x = knmtResultExtractor(options.source_file, options.target_file, options.output_file)
        x.writeTask(options.result_db)

    elif options.rnnlm:
        x = rnnlmResultExtractor(options.source_file, options.output_file)
        x.writeTask(options.result_db)
