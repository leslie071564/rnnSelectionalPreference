# -*- coding: utf-8 -*-
import sys
import argparse
from utils import getPAstr, majorityInList
from getSentence import getEventSentences
from CaseFrame import getCaseFrameXMLs
from pyknp import KNP
knp = KNP(jumanpp=True)

pa2sid = "/windroot/huang/neuralCF_data/sidSearch/cdbs/pa2sid.cdb"

class testInstance(object):
    def __init__(self, resultStr):
        self._parseResultStr(resultStr)
        self._setSentences()
        self._setBestCaseFrame()

    def _parseResultStr(self, resultStr):
        """
        build attrtibutes.
        """
        predicate, givenArgs, self.targetCase, self.targetArg, outputArgs = resultStr.split()

        self.predicate, self.predType = predicate.split(':')
        self.givenArgs = dict(map(lambda x: x.split('='), givenArgs.split('|')))
        self.outputArgs = outputArgs.split('|')

    def _setSentences(self):
        ret = getEventSentences(pa2sid)
        allArgs = [[arg, case] for case, arg in self.givenArgs.items()] + [[self.targetArg, self.targetCase]]
        paStr = getPAstr(allArgs, "%s:%s" % (self.predicate, self.predType))
        self.sentences = ret.event_to_sentence(paStr).values() 

    def _setBestCaseFrame(self):
        if self.targetCase.encode('utf-8') == u"未":
            self.caseFrameID, self.cfArgs = None, None
            return None

        self._setCaseFrameID()
        if self.caseFrameID == None:
            self.cfArgs = None
        else:
            sys.stderr.write(self.caseFrameID + '\n')
            self.cfArgs = getCaseFrameXMLs(self.caseFrameID, self.targetCase)

    def _setCaseFrameID(self):
        cf_ids = []
        for sent in self.sentences:
            cf_id = self._parseSentence(sent)
            if cf_id != None:
                cf_ids.append(cf_id)

        if cf_ids == []:
            self.caseFrameID = None
        else:
            self.caseFrameID = majorityInList(cf_ids) 

    def _parseSentence(self, sentence):
        knpResult = knp.parse(sentence.decode('utf-8'))

        for tag in knpResult.tag_list():
            # move to utilts
            tagRepname = sum(map(lambda x: x.split('/'), tag.repname.split('+')), [])
            if self.predicate in tagRepname: 
                if u"格解析結果" not in tag.features.keys():
                    continue

                caseAnalysis = tag.features[u"格解析結果"]
                pred, cf_num = caseAnalysis.split(':')[:2]
                if cf_num[1:] == u"0":
                    continue
                cf_id = "%s:%s" % (pred, cf_num)
                return cf_id
        return None

    def getSourceStr(self):
        givenArgs = ["%s %s" % (arg, case) for case, arg in self.givenArgs.items()]
        source = "%s ___ %s %s" % (" ".join(givenArgs), self.targetCase, self.predicate)
        return source

    def getColoredOutput(self):
        if not self.cfArgs:
            return '|'.join(self.outputArgs)
        coloredOutput = []
        for outputArg in self.outputArgs:
            if outputArg in self.cfArgs:
                coloredOutput.append('<font color=\"red\">%s</font>' % outputArg)
            else:
                coloredOutput.append(outputArg)

        return "|".join(coloredOutput)

    def evalByTarget(self):
        if self.targetArg in self.outputArgs:
            return 1
        else:
            return 0

    def evalByCaseFrame(self):
        if self.caseFrameID == None:
            return -1
        correct = set(self.outputArgs).intersection(self.cfArgs)
        return len(correct)

    def export(self):
        data = []
        data.append(self.getSourceStr())
        data.append(str(len(self.givenArgs)))
        data.append(self.targetCase)
        data.append(self.targetArg)

        data.append(self.getColoredOutput())

        if self.caseFrameID:
            data.append(self.caseFrameID)
        else:
            data.append("None")
        data.append(str(self.evalByTarget()))
        data.append(str(self.evalByCaseFrame()))

        data.append('<br>'.join(self.sentences))

        print "###".join(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', "--result_str", action="store", dest="result_str")
    options = parser.parse_args() 

    x = testInstance(options.result_str)
    x.export()
    
