# -*- coding: utf-8 -*-
import sys
import yaml
import unicodedata

EngCases = ['ga', 'wo', 'ni', 'to', 'de','wa', 'kara', 'yori', 'he', 'made', 'modif', 'time', 'ga2']
JapCases = [u"ガ", u"ヲ", u"ニ", u"ト", u"デ", u"未", u"カラ", u"ヨリ", u"ヘ", u"マデ", u"修飾", u"時間", u"ガ２"]
cases = dict(zip(EngCases, JapCases))

EngPreds = ['verb', 'adj', 'det']
JapPreds = [u"動", u"形", u"判"]
preds = dict(zip(EngPreds, JapPreds))

skipCategory = ['Po', 'Nd']

def rmvHiragana(phr, delimiter='+'):
    phr = phr.split(delimiter)
    phr = map(lambda x: x.split('/')[0], phr)
    return delimiter.join(phr)

def isNumberPredicate(pred):
    # modify later? 
    pred = rmvHiragana(pred.split('+')[0])
    categories = map(unicodedata.category, pred)

    #if all( c in skipCategory for c in categories ):
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

    return "%s|%s" % (args, pred)

def majorityInList(lst):
    return max(set(lst), key=lst.count)

### SQL related
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


class SQLtable(object):
    def __init__(self, c, cols, table_name):
        self.c = c
        self.cols = cols
        self.table_name = table_name
        self.set_columns()

    def set_columns(self):
        self.c.execute("CREATE TABLE %s (id TEXT PRIMARY KEY)" % (self.table_name))
        for col in self.cols:
            self.c.execute("ALTER TABLE %s ADD COLUMN \'%s\' TEXT" % (self.table_name, col))

    def set_row(self, row_data):
        self.c.execute("INSERT INTO %s VALUES (\'%s\')" % (self.table_name, "\',\'".join(row_data)))
