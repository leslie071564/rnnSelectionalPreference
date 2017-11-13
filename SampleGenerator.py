# -*- coding: utf-8 -*-
import sys
import argparse
import codecs
from utils import *

class PASextractor(object):
    def __init__(self, exp_settings):
        self._set_options(exp_settings)

    def _set_options(self, exp_settings):
        self.type = exp_settings['type']

        self.removeHiragana = exp_settings['removeHiragana']
        self.includePostfix = exp_settings['includePostfix']
        self.splitPostfix = exp_settings['splitPostfix']
        self.includeTense = exp_settings['includeTense']
        self.onlyMultiArg = exp_settings['onlyMultiArg']

        if exp_settings['sampleFormat'] == 'targetLast':
            self.targetLast, self.placeHolder = True, False
        else:
            self.targetLast, self.placeHolder = False, True

        self.targetCases = map(lambda x: cases[x], exp_settings['targetCases'])
        self.targetPreds = map(lambda x: preds[x], exp_settings['targetPreds'])

    def processLine(self, line):
        line = line.split()
        sid, rawPred, rawArgs = line[0], line[1], line[2:]

        pred = self.processPredicate(rawPred)
        args = self.processArguments(rawArgs)

        if pred == None or args == None:
            return None
        
        return sid, pred, args

    def processPredicate(self, rawPred):
        pred, predType = rawPred.split(":")
        if not self.isValidPredicate(pred, predType):
            return None

        if self.removeHiragana:
            pred = rmvHiragana(pred)

        if self.splitPostfix and '+' in pred:
            pred = " ".join(pred.split('+'))
        return pred

    def isValidPredicate(self, pred, predType):
        if predType not in self.targetPreds:
            return False

        if not self.includePostfix and '+' in pred: 
            return False

        elif not self.includeTense and '~' in pred:
            return False

        elif isNumberPredicate(pred):
            return False

        return True

    def processArguments(self, args):
        try:
            args = [[arg.split(';')[0], case.split(u'格')[0]] for arg, case in map(lambda x: x.split(":"), args)]
        except ValueError:
            return None

        args = filter(lambda x: x[1] in self.targetCases, args)
        if args == []:
            return None

        if self.onlyMultiArg and len(args) == 1:
            return None

        if self.removeHiragana:
            args = map(lambda x: [rmvHiragana(x[0]), x[1]], args)

        return args


class SampleGenerator(PASextractor):
    def __init__(self, exp_settings):
        PASextractor.__init__(self, exp_settings)

    def getMTSample(self, line):
        line = self.processLine(line)
        if line == None:
            return []
        sid, pred, args = line

        # create training instances.
        training_instances = []
        for index, arg in enumerate(args):
            arg, case = arg

            src = sum(args[:index], []) + sum(args[index + 1:], [])
            src = "%s %s %s" % (" ".join(src), pred, case)
            src = src.lstrip()
            tgt = arg
            training_instances.append([src, tgt])

        return training_instances

    def printSample(self, raw_file, output_file):
        if self.type == 'MT':
            self.printMTSample(raw_file, output_file)

        elif self.type == 'LM':
            self.printLMSample(raw_file, output_file)

    def printMTSample(self, raw_file, output_file):
        output_file = codecs.open(output_file, 'w', 'utf-8')

        with open(raw_file) as f:
            for line in f:
                line = line.decode('euc-jp').rstrip()
                training_instances = self.getMTSample(line)
                for src, tgt in training_instances:
                    output_file.write("%s###%s\n" % (src, tgt))

    def getLMSample(self, line): 
        line = self.processLine(line)
        if line == None:
            return ""
        sid, pred, args = line

        # create training instances.
        words = sum(args, []) + [pred] 
        if self.targetLast:
            words = words[::-1]
        sent = " ".join(words)

        return sent

    def printLMSample(self, raw_file, output_file):
        output_file = codecs.open(output_file, 'w', 'utf-8')

        with open(raw_file) as f:
            for line in f:
                line = line.decode('euc-jp').rstrip()
                training_instances = self.getLMSample(line)
                if training_instances == "":
                    continue
                output_file.write("%s\n" % training_instances)


class RepStrGenerator(PASextractor):
    def __init__(self, exp_settings):
        PASextractor.__init__(self, exp_settings)

    def getRepStr(self, line):
        line = self.processLine(line)
        if line == None:
            return None
        sid, pred, args = line
        repStr = getPAstr(args, pred)

        return "%s#%s" % (repStr, sid)

    def printRepFile(self, raw_file, output_file):
        output_file = codecs.open(output_file, 'w', 'utf-8')

        with open(raw_file) as f:
            for line in f:
                line = line.decode('euc-jp').rstrip()
                repStr = self.getRepStr(line)
                if repStr:
                    output_file.write("%s\n" % repStr)

    def mergeRepFile(self, processed_file, merged_file):
        merged_file = open(merged_file, 'w')

        with open(processed_file) as f:
            nowRepStr, sidList = None, []
            for line in f:
                repStr, sid = line.rstrip().split('#')
                if nowRepStr == None:
                    nowRepStr = repStr

                if repStr == nowRepStr:
                    sidList.append(sid)
                else:
                    merged_file.write("%s#%s\n" % (nowRepStr, ";".join(sidList)))
                    nowRepStr, sidList = repStr, [sid]

