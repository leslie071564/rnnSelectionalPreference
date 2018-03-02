# -*- coding: utf-8 -*-
import unicodedata

EngCases = ['ga', 'wo', 'ni', 'to', 'de','wa', 'kara', 'yori', 'he', 'made', 'modif', 'time', 'ga2']
JapCases = [u"ガ", u"ヲ", u"ニ", u"ト", u"デ", u"未", u"カラ", u"ヨリ", u"ヘ", u"マデ", u"修飾", u"時間", u"ガ２"]
cases = dict(zip(EngCases, JapCases))

EngPreds = ['verb', 'adj', 'det']
JapPreds = [u"動", u"形", u"判"]
preds = dict(zip(EngPreds, JapPreds))

skipCategory = ['Po', 'Nd']

def rmvHiraganaNaive(phr, delimiter='+'):
    if '?' in phr:
        phr = phr.split('?')[0]

    phr = phr.split(delimiter)
    phr = map(lambda x: x.split('/')[0], phr)
    return delimiter.join(phr)

def rmvHiragana(phr, delimiter='+'):
    if '?' not in phr:
        phr = phr.split(delimiter)
        phr = map(lambda x: x.split('/')[0], phr)
        return delimiter.join(phr)

    else:
        first_phr = phr.split('?')[0]
        phr_elements = first_phr.split(delimiter)

        # determine keeping kanzi or hiragana parts.
        decision_ele = None
        for ele in phr_elements:
            if '/' in ele:
                decision_ele = ele
                break

        if decision_ele != None:
            kanzi, hiragana = decision_ele.split('/')
            k_count, h_count = phr.count(kanzi + '/'), phr.count('/' + hiragana)
            keep_index = -1 if h_count > k_count else 0
        else:
            keep_index = 0

        phr_elements = map(lambda x: x.split('/')[keep_index], phr_elements)
        return delimiter.join(phr_elements)

def isNumberPredicate(pred):
    # modify later? 
    pred = rmvHiragana(pred.split('+')[0])
    categories = map(unicodedata.category, pred)

    if any( c in skipCategory for c in categories ):
        return True
    return False

def getPAstr(args, pred):
    if type(pred) == str:
        japCases = map(lambda x: x.encode('utf-8'), JapCases)
    else:
        japCases = JapCases
    args.sort(key=lambda (x, y): japCases.index(y))
    args = "|".join(sum(args, []))

    pred = pred.replace(' ', '+')

    return "%s|%s" % (args, pred)

