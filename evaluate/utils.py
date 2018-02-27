# -*- coding: utf-8 -*-
JapCases = [u"ガ", u"ヲ", u"ニ", u"ト", u"デ", u"未", u"カラ", u"ヨリ", u"ヘ", u"マデ", u"修飾", u"時間", u"ガ２"]

def getPAstr(args, pred):
    if type(pred) == str:
        japCases = map(lambda x: x.encode('utf-8'), JapCases)
    else:
        japCases = JapCases
    args.sort(key=lambda (x, y): japCases.index(y))
    args = "|".join(sum(args, []))

    pred = pred.replace(' ', '+')

    return "%s|%s" % (args, pred)

def encode_list(L):
    """
    encode a list in to the form of query string.
    ex: ['a', 'b', 'c'] => "0=a&1=b&2=c"
    """
    return "&".join(["%s=%s" % (index, element) for index, element in enumerate(L)])

def encode_dict(d):
    """
    encode a dictionary in to the form of query string.
    ex: {'k1' : 'v1', 'k2' : 'v2'} => "k1=v1&k2=v2"
    """
    return "&".join(["%s=%s" % (align, score) for align, score in d.items() if '_' not in align])

