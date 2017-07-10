#!/bin/sh
localConfig="$1"

### process config file.
type=`cat $localConfig | shyaml get-value ExpSetting.sampleType`
tmpDir=`cat $localConfig | shyaml get-value ExpLocation.PreProcess.TempDir`
pcdDir=`cat $localConfig | shyaml get-value ExpLocation.PreProcess.ProcessedDir`
expDir=`cat $localConfig | shyaml get-value ExpLocation.Exp.ExpDir`

mkdir -p $pcdDir
mkdir -p $tmpDir
mkdir -p $expDir

config=$expDir/config.yaml
cp $localConfig $config
echo "config file: $config"


### extract training samples
# use gxp
preProcessScript=`cat $config | shyaml get-value Scripts.preProcessScript`
python $preProcessScript -o ./preProcess.task --config $config --print_task_file
gxpc js -a work_file=preProcess.task -a cpu_factor=0.5
rm -f ./preProcess.task

# merge files
pcdPrefix=`cat $config | shyaml get-value ExpLocation.PreProcess.ProcessedPrefix`
pcdFile=`cat $config | shyaml get-value ExpLocation.PreProcess.ProcessedFile`

for f in $pcdPrefix*; do
    echo $f;
    cat $f >> $pcdFile
done

# uniq globally
$NICE sort --parallel=10 -u -o $pcdFile $pcdFile

# shuffle
echo shuffling...
shuf $pcdFile --output=$pcdFile


### setup experiment directory
expDataDir=`cat $config | shyaml get-value ExpLocation.Exp.DataDir`
expTrainDir=`cat $config | shyaml get-value ExpLocation.Exp.TrainDir`
mkdir -p $expDataDir
mkdir -p $expTrainDir

devNum=10001
testNum=20001

if [ "$type" = "MT" ] ; then
    # seperate the sampel into dev/test/train sets.
    srcDev=$expDataDir/source_dev.txt
    srcTest=$expDataDir/source_test.txt
    srcTrain=$expDataDir/source_train.txt
    tgtDev=$expDataDir/target_dev.txt
    tgtTest=$expDataDir/target_test.txt
    tgtTrain=$expDataDir/target_train.txt

    csplit $pcdFile $devNum $testNum
    $NICE awk -F"###" '{print $1 > "'"$srcDev"'"; print $2 > "'"$tgtDev"'"}' xx00
    $NICE awk -F"###" '{print $1 > "'"$srcTest"'"; print $2 > "'"$tgtTest"'"}' xx01
    $NICE awk -F"###" '{print $1 > "'"$srcTrain"'"; print $2 > "'"$tgtTrain"'"}' xx02
    rm -f xx*

    # print commands.
    dataPrefix=$expDataDir/data_knmt
    trainPrefix=$expTrainDir/rnnSP

    cmd="knmt make_data $srcTrain $tgtTrain $dataPrefix --dev_src $srcDev --dev_tgt $tgtDev --test_src $srcTest --test_tgt $tgtTest"
    echo "***** Run the following command to make data for knmt processing:"
    echo $cmd

    cmd="knmt train $dataPrefix $trainPrefix --mb_size 512 --gpu GPU"
    echo "***** Run the following command to train knmt model (substitute GPU to the real number of GPU):"
    echo $cmd
        
elif [ "$type" = "LM" ] ; then
    # seperate the sampel into test/train sets.
    pcdDev=$expDataDir/dev.txt
    pcdTest=$expDataDir/test.txt
    pcdTrain=$expDataDir/train.txt

    csplit $pcdFile $devNum $testNum
    mv xx00 $pcdDev
    mv xx01 $pcdTest
    mv xx02 $pcdTrain

    # print commands.
    model_name=$expTrainDir/lang.mdl

    cmd="./rnnlm -rnnlm $model_name -train $pcdTrain -valid $pcdDev --nce 22 --hidden 100 --direct 100 --direct-order 3 -bptt 4 --use-cuda 1"
    echo "***** Run the following command to train RNNLM model:"
    echo $cmd
fi

