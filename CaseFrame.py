# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/home/huang/work/CDB_handler')
from CDB_Reader import CDB_Reader
from utils import rmvHiragana
import xml.etree.ElementTree as ET
CF_DB = "/violet/share/cf/20160205/cf.xml.cdb.keymap"


def getCaseFrameXMLs(cf_id, targetCase):
    predicate, predType = cf_id.split(':')
    cfNum = str(predType[1:])
    predType = predType[0]
    targetCase += u"格"

    cf_cdb = CDB_Reader(CF_DB, repeated_keys=True)
    xml = cf_cdb.get(predicate, exhaustive=True)
    for xml_predType in xml:
        predOfType = ET.fromstring(xml_predType)[0]
        if predOfType.attrib['predtype'] != predType:
            continue

        for predOfNum in predOfType:
            if predOfNum.attrib['id'] != cf_id:
                continue
            else:
                args = getTargetArgs(predOfNum, targetCase)
                return args
    sys.stderr.write("didn't find case frame of id: %s\n" % cf_id)
    return []

def getTargetArgs(predOfNum, targetCase, threshold=5):
    argsAboveThreshold = []

    for caseArgs in predOfNum:
        for arg in caseArgs:
            try:
                arg_text = rmvHiragana(arg.text.encode('utf-8'))
                arg_freq = int(arg.attrib['frequency'])
            except:
                sys.stderr.write("having problem converting argument: %s\n" % (arg.text.encode('utf-8')))

            if arg_freq >= threshold:
                #print arg_text, arg_freq
                argsAboveThreshold.append(arg_text)
        break

    return argsAboveThreshold


"""
if __name__ == "__main__":
    case = u"デ格"
    cf_id = u"必要だ/ひつようだ:形8"

    getCaseFrameXMLs(cf_id, case)
"""
