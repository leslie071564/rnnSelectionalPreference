#!/bin/bash
NICE="nice -n 19"
config_file=$1
expDataDir=`cat $config_file | shyaml get-value ExpLocation.expDataDir`
expTrainDir=`cat $config_file | shyaml get-value ExpLocation.expTrainDir`
expResultDir=`cat $config_file | shyaml get-value ExpLocation.expResultDir`
resultTempDir=$expResultDir/result_tmp

type=`cat $config_file | shyaml get-value ExpSetting.type`

### extract raw result to unified form.
if [ "$type" = "MT" ] ; then
    test_source_file=$expDataDir/source_test.txt
    test_target_file=$expDataDir/target_test.txt
    output_file=$expResultDir/output_10best.txt

    python generate_result.py -s $test_source_file -t $test_target_file -o $output_file -r $resultTempDir --knmt
elif [ "$type" = "LM" ] ; then
    test_file=$expDataDir/test.txt
    output_file=$expResultDir/output_10best.txt

    python generate_result.py -s $test_file -o $output_file -r $resultTempDir --rnnlm
fi

task_file=./generate_result.task
result_file=$expResultDir/result.txt
gxpc js -a work_file=generate_result.task a cpu_factor=0.25 
cat $resultTempDir/*/*.txt > $result_file
rm -rf $resultTempDir
rm -f $task_file 

### write to result db.
result_db=$expResultDir/result.sqlite
python write_html_db.py -r $result_file -d $result_db 
echo experiment result saved to $result_db
