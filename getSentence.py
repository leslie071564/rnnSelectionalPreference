# -*- coding: utf-8 -*-
import sys
import os.path
import cdb
from CDB_Reader import CDB_Reader

class getEventSentences(object):
    pa_sid_cdb = "/pear/huang/rnnSelectionalPreference/180125_rep/tmp/ev_sid.cdb.keymap"
    sentence_cdb_dir = "/pear/share/www-uniq/v2006-2015.text-cdb"

    def __init__(self, pa_sid_cdb=None, sentence_cdb_dir=None):
        if pa_sid_cdb != None:
            self.pa_sid_cdb = pa_sid_cdb
        self.pa_sid_cdb = CDB_Reader(self.pa_sid_cdb)

        if sentence_cdb_dir != None:
            self.sentence_cdb_dir = sentence_cdb_dir

    def events_to_sentence(self, ev_list):
        """
        input:
            ev_list: input a list of rep_strs which serves as the key to ev-sid cdb.
        return:
            sents: list of raw sentences.
        """
        sids = self.events_to_sids(ev_list)

        sents = []
        for sid in sids:
            sent = self.sid_to_sentence(sid)
            if sent == None:
                sys.stderr.write("Sentence not found: %s\n" % sid)
                continue

            sents.append(sent)

        return sents

    def events_to_sids(self, ev_list):
        """
        input:
            ev_list: input a list of rep_strs which serves as the key to ev-sid cdb.
        return:
            sids: list of sids.
        """
        sid_lists = [ self.pa_sid_cdb.get(key, exhaustive=True) for key in ev_list ]

        if None in sid_lists:
            return []

        sid_lists = [ set(sids.split(';')) for sids in sid_lists ]
        sids = set.intersection(*sid_lists)

        return sids

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

