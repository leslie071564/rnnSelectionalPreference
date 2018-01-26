# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
from itertools import izip
import utils
KATA_CASE = [x.encode('utf-8') for x in [u'ガ', u"ヲ", u"ニ", u"デ", u"未"]]
from SentenceExtractor import SentenceExtractor

class knmtResultExtractor(object):
    def __init__(self, sourceFile, targetFile, outputFile):
        self.sentenceExtractor = SentenceExtractor()
        self._setResultData(sourceFile, targetFile, outputFile)

    def _setResultData(self, sourceFile, targetFile, outputFile):
        self.resultData = defaultdict(dict)

        self._processTestFile(sourceFile, targetFile)
        self._processOutputFile(outputFile)

    def _processTestFile(self, sourceFile, targetFile):
        for index, (src, tgt) in enumerate(izip(open(sourceFile, 'rb'), open(targetFile, 'rb'))):
            src, tgt = src.rstrip(), tgt.rstrip()
            srcStructure = self._get_src_structure(src)

            self.resultData[index].update({'s': srcStructure, 't': tgt})

    def _get_src_structure(self, raw_src):
        PAs = raw_src.split('END')

        srcStructure = []
        for index, pa_str in enumerate(PAs):
            is_target_pa = (index == len(PAs) - 1)
            this_src = self._process_src(pa_str, detect_target_case=is_target_pa)
            srcStructure.append(this_src)

        return srcStructure

    def _process_src(self, raw_src, detect_target_case=False):
        src_dic = {}
        # save target case if needed.
        if detect_target_case:
            targetCase = raw_src.split()[-1]
            raw_src = " ".join(raw_src.split()[:-1])

            src_dic['tgt'] = targetCase

        # save arguments and predicate.
        words = raw_src.split()
        last_case_index = -1
        for index, word in enumerate(words):
            if word in KATA_CASE:
                arg, case = words[index - 1], word
                src_dic[case] = arg
                last_case_index = index

        pred = '+'.join(words[last_case_index + 1:])
        src_dic['pred'] = pred

        return src_dic

    def _processOutputFile(self, outputFile):
        now_index, out_args = 0, []
        for line in open(outputFile, 'rb').readlines():
            index, out = line.rstrip().split(' ||| ')
            index = int(index)
            out = "UNK" if "UNK" in out else out

            if index == now_index:
                out_args.append(out)
            else:
                self.resultData[now_index]['o'] = out_args
                now_index, out_args = index, []

        # last index
        self.resultData[index]['o'] = out_args

    def export_result(self, result_db_cursor):
        for index in self.resultData:
            row_data = self.convert_result_data(index)
            result_db_cursor.execute(**row_data)

            sys.stderr.write("%s written\n" % index)

    def convert_result_data(self, index):
        index_data = self.resultData[index]
        
        row_data = {}
        # source-related
        source_struc = index_data['s']
        row_data['source_rep'] = self._get_source_str(source_struc)

        pred_list = [src_dic['pred'] for src_dic in source_struc]
        row_data['pred_list'] = utils.encode_list(pred_list)

        arg_list = self._get_arg_list(source_struc)
        row_data['arg_list'] = utils.encode_list(arg_list)

        # output-related
        output_list = index_data['o']
        row_data['output_list'] = utils.encode_list(index_data['o'])

        # target-related
        target_arg = index_data['t']
        row_data['target_arg'] = target_arg
        row_data['target_case'] = source_struc[-1]['tgt']
        row_data['target_pred'] = source_struc[-1]['pred']

        # other attributes
        rep_strs = self._get_rep_strs(source_struc, target_arg)
        sents = self.sentenceExtractor.events_to_sentence(rep_strs)
        row_data['raw_sents'] = "<br>".join(sents)

        row_data = {k: v.decode('utf-8') for k, v in row_data.iteritems()}
        return row_data

    def _get_rep_strs(self, src_struc, target_arg):
        rep_strs = []
        for src_dic in src_struc:
            pred = src_dic['pred']
            args = [ [arg, case] for case, arg in src_dic.items() if case not in ['pred', 'tgt'] ]
            if 'tgt' in src_dic:
                args.append([target_arg, src_dic['tgt']])

            rep_str = utils.getPAstr(args, pred)
            rep_strs.append(rep_str)

        return rep_strs

    def _get_source_str(self, srcStructure):
        strs = []
        for src_dic in srcStructure:
            this_src_str = ""

            for case, arg in src_dic.iteritems():
                if case in ['tgt', 'pred']:
                    continue
                this_src_str += "%s %s " % (arg, case)

            this_src_str += src_dic['pred']
            if 'tgt' in src_dic:
                this_src_str = "______ %s %s" % (src_dic['tgt'], this_src_str)

            strs.append(this_src_str)
            
        source_str = "<br>".join(strs)
        return source_str

    def _get_arg_list(self, srcStructure):
        args = []
        for src_dic in srcStructure:
            args += [arg for case, arg in src_dic.iteritems() if case not in ['pred', 'tgt']]

        return args

class rnnlmResultExtractor(object):
    def __init__(self, testFile, outputFile):
        pass
