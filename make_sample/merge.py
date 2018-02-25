# -*- coding: utf-8 -*-
import sys

def merge(input_fn, merged_file):
    merged_file = open(merged_file, 'w')
    with open(input_fn) as f:
        nowRepStr, sidList = None, []
        for line in f:
            repStr, sid = line.rstrip().split('###')
            if nowRepStr == None:
                nowRepStr = repStr

            if repStr == nowRepStr:
                sidList.append(sid)
            else:
                merged_file.write("%s###%s\n" % (nowRepStr, ";".join(sidList)))
                nowRepStr, sidList = repStr, [sid]

if __name__ == "__main__":
    input_fn, merged_file = sys.argv[1], sys.argv[2]
    
    merge(input_fn, merged_file)

