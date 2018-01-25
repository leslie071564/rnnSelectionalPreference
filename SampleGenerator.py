# -*- coding: utf-8 -*-
import sys
import argparse
import codecs
from utils import *

class PASextractor(object):
    def __init__(self, exp_settings):
        self.config = exp_settings

    def processLine(self, line):
        sid, PAs = line.split(" ", 1)

        pa_elements = []
        for PA in PAs.split("#"):
            rawPred, rawArgs = PA.split(" ", 1)
            pred = self.processPredicate(rawPred)
            args = self.processArguments(rawArgs)

            if pred == None or args == None:
                continue
            pa_elements.append([pred, args])

        return pa_elements
        

    def processPredicate(self, rawPred):
        pred, predType = rawPred.split(":")
        if not self.isValidPredicate(pred, predType):
            return None

        if self.config.removeHiragana:
            pred = rmvHiragana(pred)

        if self.config.splitPostfix and '+' in pred:
            pred = " ".join(pred.split('+'))
        return pred

    def isValidPredicate(self, pred, predType):
        if predType not in self.config.targetPreds:
            return False

        if not self.config.includePostfix and '+' in pred: 
            return False

        elif not self.config.includeTense and '~' in pred:
            return False

        elif isNumberPredicate(pred):
            return False

        return True

    def processArguments(self, args):
        args = args.split(" ")
        try:
            args = [[arg.split(';')[0], case.split(u'格')[0]] for arg, case in map(lambda x: x.split(":"), args)]
        except ValueError:
            return None

        args = filter(lambda x: x[1] in self.config.targetCases, args)
        if args == []:
            return None

        if self.config.onlyMultiArg and len(args) == 1:
            return None

        if self.config.removeHiragana:
            args = map(lambda x: [rmvHiragana(x[0]), x[1]], args)

        return args

    def get_pa_rep(self, pa):
        pred, args = pa
        args = ["%s %s" % (arg, case) for arg, case in args]
        return "%s %s".lstrip() % (" ".join(args), pred)

    def get_pa_training_instance(self, pa):
        pred, args = pa
        args = ["%s %s" % (arg, case) for arg, case in args]
        training_instances = []
        for index, arg in enumerate(args):
            arg, case = arg.split()
            src_args = " ".join(arg for arg_index, arg in enumerate(args) if arg_index != index)
            src = "%s %s %s" % (src_args, pred, case)
            tgt = arg
            training_instances.append([src.lstrip(), tgt])
        return training_instances


class SampleGenerator(PASextractor):
    def __init__(self, exp_settings):
        PASextractor.__init__(self, exp_settings)

    def getMTSample(self, line):
        pas = self.processLine(line)
        if pas == []:
            return []

        # create training instances.
        training_instances = []
        for index, this_pa in enumerate(pas):
            other_pas = " END ".join(self.get_pa_rep(pa) for pa_index, pa in enumerate(pas) if pa_index != index)
            pred, args = this_pa

            pa_training_instances = self.get_pa_training_instance(this_pa)
            if other_pas == "":
                training_instances += pa_training_instances
            else:
                training_instances += [ ["%s END %s" % (other_pas, src), tgt] for src, tgt in pa_training_instances]

        return training_instances

    def getREP(self, line):
        pas = self.processLine(line)
        reps = [self.get_pa_rep(pa) for pa in pas]
        return reps

    def printSample(self, raw_file, output_file):
        if self.config.type == 'MT':
            self.printMTSample(raw_file, output_file)

        elif self.config.type == 'LM':
            self.printLMSample(raw_file, output_file)

        elif self.config.type == 'REP':
            self.print_sample_representation_str(raw_file, output_file)

    def print_sample_representation_str(self, raw_file, output_file):
        output_file = codecs.open(output_file, 'w', 'utf-8')

        with open(raw_file) as f:
            for line in f:
                line = line.decode('euc-jp').rstrip()
                sid = line.split()[0]
                reps = self.getREP(line)
                for rep in reps:
                    output_file.write("%s###%s\n" % (rep, sid))

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
        if self.config.targetLast:
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

