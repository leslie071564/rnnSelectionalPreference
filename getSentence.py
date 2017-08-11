# -*- coding: utf-8 -*-
import sys
import cdb
from CDB_Reader import CDB_Reader
import os.path
import argparse

class getEventSentences(object):
    sentence_cdb_dir = "/pear/share/www-uniq/v2006-2015.text-cdb"
    def __init__(self, pa2sid):
        self.pa2sid = pa2sid + '.keymap'

    def sid_to_sentence(self, sid):
        sid = sid.split(':')[-1]
        sub_dirs = sid.split('-')
        if sub_dirs[0] == "w201103":
            if sub_dirs[1] == "":
                sub_dirs[0] = "w201103.old/%s" % (sub_dirs[2])
                sub_dirs.pop(1)
            else:
                sub_dirs[0] = "w201103/%s" % sub_dirs[1]
            sub_dirs.pop(1)

        which_cdb = "%s/%s/%s/%s.cdb" % (getEventSentences.sentence_cdb_dir, sub_dirs[0], "/".join(sub_dirs[1][:3]), sub_dirs[1][:4])
        if not os.path.isfile(which_cdb):
            sys.stderr.write("cdb file not found for %s.\n" % sid)
            return None
        c = cdb.init(which_cdb)
        return c[sid]

    def event_to_sentence(self, event):
        #c = cdb.init(self.pa2sid)
        c = CDB_Reader(self.pa2sid)
        sids = c.get(event)
        if sids == None:
            return {}
        sids = sids.split(';')

        sents = {}
        for sid in sids:
            sent = self.sid_to_sentence(sid)
            if sent == None:
                continue
            sents[sid] = sent
        return sents


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', "--event", action="store", dest="event")
    parser.add_argument('-b', "--html", action="store_true", default=False, dest="html")
    options = parser.parse_args() 

    #pa2sid = "/windroot/huang/neuralCF_data/sidSearch_main/pa2sid.cdb"
    pa2sid = "/windroot/huang/neuralCF_data/sidSearch/cdbs/pa2sid.cdb"

    ret = getEventSentences(pa2sid)
    sents = ret.event_to_sentence(options.event)

    print "\n".join(['[%s] %s' % x for x in sents.items()])
