#!/bin/bash
NICE="nice -n 19"
config_file=$1
expDataDir=`cat $config_file | shyaml get-value ExpLocation.expDataDir`
expTrainDir=`cat $config_file | shyaml get-value ExpLocation.expTrainDir`
expResultDir=`cat $config_file | shyaml get-value ExpLocation.expResultDir`

type=`cat $config_file | shyaml get-value ExpSetting.type`

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
evaluate_script=$SCRIPTPATH/evaluate.py

### extract raw result to unified form.
if [ "$type" = "MT" ] ; then
    test_source_file=$expDataDir/source_test.txt
    test_target_file=$expDataDir/target_test.txt
    output_file=$expResultDir/output.txt
    result_db_loc=$expResultDir/result.sqlite

    python $evaluate_script -s $test_source_file -t $test_target_file -o $output_file -r $result_db_loc --knmt "${@:2}"
elif [ "$type" = "LM" ] ; then
    test_file=$expDataDir/test.txt
    output_file=$expResultDir/output.txt
    result_db_loc=$expResultDir/result.sqlite

    python $evaluate_script -s $test_file -o $output_file -r $result_db_loc --rnnlm
fi

