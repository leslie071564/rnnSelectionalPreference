# -*- coding: utf-8 -*-
import sys
import argparse
import codecs
from utils import *

class PASextractor(object):
    def __init__(self, exp_settings):
        self.config = exp_settings
        self.intrans_list = [ pred.rstrip().decode('utf-8') for pred in open(exp_settings.intrans_list_file, 'r') ]

    def processLine(self, line):
        sid, PAs = line.split(" ", 1)

        pa_elements = []
        for PA in PAs.split("#"):
            rawPred, rawArgs = PA.split(" ", 1)
            pred = self.processPredicate(rawPred)
            args = self.processArguments(rawArgs)

            if pred == None or args == None:
                continue

            if self.config.extractIntrans and rawPred in self.intrans_list:
                args.append( ('INTRANS', u'ヲ') )

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
        args = ["%s %s" % (arg, case) for arg, case in args if arg != "INTRANS"]
        return "%s %s".lstrip() % (" ".join(args), pred)

    def get_pa_training_instance(self, pa):
        pred, args = pa
        args = ["%s %s" % (arg, case) for arg, case in args]

        training_instances = []
        for index, arg in enumerate(args):
            arg, case = arg.split()
            src_args = " ".join(sArg for arg_index, sArg in enumerate(args) if arg_index != index and not sArg.startswith("INTRANS"))
            src = "%s %s %s" % (src_args, pred, case)
            tgt = arg
            training_instances.append([src.lstrip(), tgt])

        return training_instances


class SampleGenerator(PASextractor):
    def __init__(self, exp_settings):
        PASextractor.__init__(self, exp_settings)

    def printSample(self, raw_file, output_file):
        if self.config.type == 'MT':
            self.printMTSample(raw_file, output_file)

        elif self.config.type == 'LM':
            self.printLMSample(raw_file, output_file)

        elif self.config.type == 'REP':
            self.printSampleRepStr(raw_file, output_file)

    def printMTSample(self, raw_file, output_file):
        output_file = codecs.open(output_file, 'w', 'utf-8')

        with open(raw_file) as f:
            for line in f:
                line = line.decode('euc-jp').rstrip()
                training_instances = self.getMTSample(line)
                for src, tgt in training_instances:
                    output_file.write("%s###%s\n" % (src, tgt))

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

    def printLMSample(self, raw_file, output_file):
        output_file = codecs.open(output_file, 'w', 'utf-8')

        with open(raw_file) as f:
            for line in f:
                line = line.decode('euc-jp').rstrip()
                training_instances = self.getLMSample(line)
                if training_instances == "":
                    continue
                output_file.write("%s\n" % training_instances)

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

    def printSampleRepStr(self, raw_file, output_file):
        output_file = codecs.open(output_file, 'w', 'utf-8')

        with open(raw_file) as f:
            for line in f:
                line = line.decode('euc-jp').rstrip()
                sid = line.split()[0]

                for pred, args in self.processLine(line):
                    rep = getPAstr(args, pred)
                    output_file.write("%s###%s\n" % (rep, sid))

