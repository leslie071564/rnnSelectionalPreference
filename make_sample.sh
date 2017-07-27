#!/bin/sh
NICE="nice -n 19"

rawPrefix=$1
sampleFile=$2
config_file=$sampleFile.make_sample_config.yaml
task_file='./preProcess.task'

# generate config file.
python make_sample.py print_config "$@" --config $config_file

# extract training samples from each raw file.
python make_sample.py print_task --config $config_file --task_file $task_file

gxpc js -a work_file=preProcess.task -a cpu_factor=0.5
rm -f $task_file

# merge and uniq to prepare final sample file.
tmpPrefix=`cat $config_file | shyaml get-value ExpLocation.tmpPrefix`
for f in $tmpPrefix*; do
    echo $f;
    cat $f >> $sampleFile
done

$NICE sort --parallel=10 -u -o $sampleFile $sampleFile

