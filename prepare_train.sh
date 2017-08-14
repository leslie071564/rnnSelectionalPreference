#!/bin/sh
NICE="nice -n 19"

sampleFile=$1
expDir=$2
config_file=$expDir/train_config.yaml
mkdir -p $expDir

python prepare_train_config.py "$@" --config $config_file

# get options
expDataDir=`cat $config_file | shyaml get-value ExpLocation.expDataDir`
expTrainDir=`cat $config_file | shyaml get-value ExpLocation.expTrainDir`
expResultDir=`cat $config_file | shyaml get-value ExpLocation.expResultDir`
mkdir -p $expDataDir $expTrainDir $expResultDir

type=`cat $config_file | shyaml get-value ExpSetting.type`

devSize=`cat $config_file | shyaml get-value ExpSetting.devSize`
testSize=`cat $config_file | shyaml get-value ExpSetting.testSize`
devNum=$(( devSize + 1 ))
testNum=$(( devSize + testSize + 1 ))

# shuffle
expSampleFile=$expDataDir/all.txt
shuf $sampleFile --output=$expSampleFile

# split file
if [ "$type" = "MT" ] ; then
    # seperate the sampel into dev/test/train sets.
    srcDev=$expDataDir/source_dev.txt
    srcTest=$expDataDir/source_test.txt
    srcTrain=$expDataDir/source_train.txt
    tgtDev=$expDataDir/target_dev.txt
    tgtTest=$expDataDir/target_test.txt
    tgtTrain=$expDataDir/target_train.txt

    csplit $expSampleFile $devNum $testNum
    $NICE awk -F"###" '{print $1 > "'"$srcDev"'"; print $2 > "'"$tgtDev"'"}' xx00
    $NICE awk -F"###" '{print $1 > "'"$srcTest"'"; print $2 > "'"$tgtTest"'"}' xx01
    $NICE awk -F"###" '{print $1 > "'"$srcTrain"'"; print $2 > "'"$tgtTrain"'"}' xx02
    rm -f xx*

    # print commands.
    dataPrefix=$expDataDir/knmt
    trainPrefix=$expTrainDir/knmt

    cmd="knmt make_data $srcTrain $tgtTrain $dataPrefix --dev_src $srcDev --dev_tgt $tgtDev --test_src $srcTest --test_tgt $tgtTest"
    echo "***** Run the following command to make data for knmt processing:"
    echo $cmd

    cmd="knmt train $dataPrefix $trainPrefix --mb_size 512 --gpu GPU"
    echo "***** Run the following command to train knmt model (substitute GPU to the real number of GPU):"
    echo $cmd

    model=$trainPrefix.model.best_loss.npz
    model_config=$trainPrefix.train.config
    output_file=$expResultDir/output.txt

    cmd="knmt eval $model_config $model $srcTest $output_file --mode beam_search --nbest 10"
    echo "***** Run the following command to prepare output (10-best) file:"
    echo $cmd
        
elif [ "$type" = "LM" ] ; then
    # seperate the sampel into test/train sets.
    pcdDev=$expDataDir/dev.txt
    pcdTest=$expDataDir/test.txt
    pcdTrain=$expDataDir/train.txt

    csplit $expSampleFile $devNum $testNum
    mv xx00 $pcdDev
    mv xx01 $pcdTest
    mv xx02 $pcdTrain

    # print commands.
    model_name=$expTrainDir/rnnlm.mdl
    output_file=$expResultDir/output.txt

    cmd="./rnnlm -rnnlm $model_name -train $pcdTrain -valid $pcdDev --nce 22 --hidden 100 --direct 100 --direct-order 3 -bptt 4 --use-cuda 1"
    echo "***** Run the following command to train RNNLM model:"
    echo $cmd

    cmd="./rnnlm -rnnlm $model_name --test $pcdTest --nce-accurate-test 1 --use-cuda 0 > $output_file"
    echo "***** Run the following command to prepare output (10-best) file:"
    echo $cmd
fi

