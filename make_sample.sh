#!/bin/sh
NICE="nice -n 19"

rawPrefix=$1
sampleDir=$2

# generate config file.
mkdir -p $sampleDir
config_file=$sampleDir/make_sample_config.yaml
python make_sample.py print_config "$@" --config $config_file

# mkdir: temporary directories.
sampleTmpDir=`cat $config_file | shyaml get-value ExpLocation.sampleTmpDir`
mkdir -p $sampleTmpDir
parallelTmpDir=`cat $config_file | shyaml get-value ExpLocation.parallelTmpDir`
gxpc e mkdir -p $parallelTmpDir

# extract training samples from each raw file.
task_file='./preProcess.task'
python make_sample.py print_task --config $config_file --task_file $task_file
gxpc js -a work_file=preProcess.task -a cpu_factor=0.125
echo "sample files extracted in directory: $sampleTmpDir"

# merge and uniq to prepare final sample file.
sampleFile=$sampleDir/all_samples.txt
rm -f $sampleFile
for f in $sampleTmpDir/*; do
    echo $f;
    cat $f >> $sampleFile
done

# sort and uniq samples.
echo "merging all sample files into: $sampleFile ..."
sort_tmp_dir=/data/huang/tmp_sort
mkdir -p $sort_tmp_dir

type=`cat $config_file | shyaml get-value ExpSetting.type`
if [ "$type" = "REP" ] ; then
    $NICE sort --parallel=10 -u --temporary-directory=$sort_tmp_dir -o $sampleFile $sampleFile
    tmp_sample_file=$sampleFile.tmp
    python ./merge.py $sampleFile $tmp_sample_file && mv $tmp_sample_file $sampleFile 

    ev_sid_cdb_prefix=$sampleDir/ev_sid.cdb
    python ./build_sentence_db.py -i $sampleFile -o $ev_sid_cdb_prefix
    echo "event-sid cdb build at: $ev_sid_cdb_prefix"
else
    $NICE sort --parallel=10 -u --temporary-directory=$sort_tmp_dir -o $sampleFile $sampleFile

    echo "all samples sorted and uniqed into file: $sampleFile"
fi

# clean-up
rm -f $task_file
rm -rf $sampleTmpDir
rm -rf $sort_tmp_dir
gxpc e rm -rf $parallelTmpDir

