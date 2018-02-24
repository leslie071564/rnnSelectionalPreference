#!/bin/sh
NICE="nice -n 19"

sampleFile=$1
expDir=$2

## get options from config file.
mkdir -p $expDir
python prepare_train_config.py "$@"
config_file=$expDir/train_config.yaml

# experiment directories and mkdir.
trainingGraph=`cat $config_file | shyaml get-value ExpLocation.trainingGraph`
expDataDir=`cat $config_file | shyaml get-value ExpLocation.expDataDir`
expTrainDir=`cat $config_file | shyaml get-value ExpLocation.expTrainDir`
expResultDir=`cat $config_file | shyaml get-value ExpLocation.expResultDir`
mkdir -p $expDataDir $expTrainDir $expResultDir

# other options.
type=`cat $config_file | shyaml get-value ExpSetting.type`
UNKfilter=`cat $config_file | shyaml get-value ExpSetting.UNKfilter`

tgtVocSize=`cat $config_file | shyaml get-value ExpSetting.tgtVoc`
srcVocSize=`cat $config_file | shyaml get-value ExpSetting.srcVoc`

devSize=`cat $config_file | shyaml get-value ExpSetting.devSize`
testSize=`cat $config_file | shyaml get-value ExpSetting.testSize`
trainSize=`cat $config_file | shyaml get-value ExpSetting.trainSize`


## shuffle and extract portion of training samples into $expSampleFile.

# shuffle and get the portion of data for training.
echo "shuffling ..."
expSampleFile=$expDataDir/all.txt
trainNum=$(( devSize + testSize + trainSize ))
shuf $sampleFile -n $trainNum --output=$expSampleFile

# contraint on length of line.
echo "filtering out too-long training samples ..."
tmpFile=$expSampleFile.tmp
awk 'NF<=100' $expSampleFile > $tmpFile
mv $tmpFile $expSampleFile


## remove samples which have UNK in the target side.
if [ "$UNKfilter" = "True" ] ;
then
    # generate list of frequent target words.
    tgtCountFile=$expDataDir/tgt_counts.txt
    frequentTgtFile=$expDataDir/tgt_frequent.txt

    echo "counting target-side word frequencies"
    awk -F'###' '{count[$2]++} END {for (word in count) print word, count[word]}' $expSampleFile > $tgtCountFile
    sort -nr -k2,2 $tgtCountFile -o $tgtCountFile
    head -n $tgtVocSize $tgtCountFile > $frequentTgtFile

    #remove samples with non-frequent words on the target side.
    filteredSampleFile=$expDataDir/all_without_unk.txt
    python ./remove_unk_tgt.py $expDataDir > $filteredSampleFile
    mv $filteredSampleFile $expSampleFile
    echo "filtered samples with UNK"

fi


## split file and output commands.

if [ "$type" = "MT" ] ; then
    # seperate samples into dev/test/train sets.
    csplit -f $expDataDir/sample $expSampleFile $((devSize + 1)) $((devSize + testSize + 1))

    devSet=$expDataDir/sample00
    testSet=$expDataDir/sample01
    trainSet=$expDataDir/sample02

    # seperate the sampel into dev/test/train sets.
    srcDev=$expDataDir/source_dev.txt
    srcTest=$expDataDir/source_test.txt
    srcTrain=$expDataDir/source_train.txt
    tgtDev=$expDataDir/target_dev.txt
    tgtTest=$expDataDir/target_test.txt
    tgtTrain=$expDataDir/target_train.txt

    $NICE awk -F"###" '{print $1 > "'"$srcDev"'"; print $2 > "'"$tgtDev"'"}' $devSet
    $NICE awk -F"###" '{print $1 > "'"$srcTest"'"; print $2 > "'"$tgtTest"'"}' $testSet
    $NICE awk -F"###" '{print $1 > "'"$srcTrain"'"; print $2 > "'"$tgtTrain"'"}' $trainSet

    rm -f $devSet $testSet $trainSet

    # print commands.
    dataPrefix=$expTrainDir/knmt_data
    trainPrefix=$expTrainDir/knmt_train

    cmd="knmt make_data $srcTrain $tgtTrain $dataPrefix --dev_src $srcDev --dev_tgt $tgtDev --test_src $srcTest --test_tgt $tgtTest --src_voc_size $srcVocSize --tgt_voc_size $tgtVocSize"
    echo "***** Run the following command to make data for knmt processing:"
    echo $cmd

    cmd="knmt train $dataPrefix $trainPrefix --mb_size 512 --gpu GPU"
    echo "***** Run the following command to train knmt model (substitute GPU to the real number of GPU):"
    echo $cmd

    cmd="knmt utils graph $trainPrefix.result.sqlite $trainingGraph"
    echo "***** Run the following command to output training graph:"
    echo $cmd

    model=$trainPrefix.model.best_loss.npz
    model_config=$trainPrefix.train.config
    output_file=$expResultDir/output.txt

    cmd="knmt eval $model_config $model $srcTest $output_file --mode beam_search --nbest 10"
    echo "***** Run the following command to prepare output (10-best) file:"
    echo $cmd
        
elif [ "$type" = "LM" ] ; then
    # seperate the sampel into test/train sets.
    csplit -f $expDataDir/sample $expSampleFile $((devSize + 1)) $((devSize + testSize + 1))

    devSample=$expDataDir/dev.txt
    testSample=$expDataDir/test.txt
    trainSample=$expDataDir/train.txt
    mv $expDataDir/sample00 $devSample
    mv $expDataDir/sample01 $testSample
    mv $expDataDir/sample02 $trainSample

    # print commands.
    model_name=$expTrainDir/rnnlm.mdl
    output_file=$expResultDir/output.txt

    cmd="./rnnlm -rnnlm $model_name -train $trainSample -valid $devSample --nce 22 --hidden 100 --direct 100 --direct-order 3 -bptt 4 --use-cuda 1"
    echo "***** Run the following command to train RNNLM model:"
    echo $cmd

    cmd="./rnnlm -rnnlm $model_name --test $testSample --nce-accurate-test 1 --use-cuda 0 > $output_file"
    echo "***** Run the following command to prepare output (10-best) file:"
    echo $cmd
fi

