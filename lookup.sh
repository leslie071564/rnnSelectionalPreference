#!/bin/sh
NICE="nice -n 19"

train_config=$1
inputFile=$2
outputFile=$3

expTrainDir=`cat $train_config | shyaml get-value ExpLocation.expTrainDir`
expDataDir=`cat $train_config | shyaml get-value ExpLocation.expDataDir`
type=`cat $train_config | shyaml get-value ExpSetting.type`

if [ "$type" = "MT" ] ; then
    # split input file into source/candidate file.
    tmp_src_file=$inputFile.src
    $NICE awk -F"###" '{ print $2 > "'"$tmp_src_file"'" }' $inputFile

    # get scores for every word in the vocabuulary.
    trainPrefix=$expTrainDir/knmt
    model=$trainPrefix.model.best_loss.npz
    model_config=$trainPrefix.train.config
    tmp_translate_file=$inputFile.tmp.out
    score_file=$inputFile.score

    knmt eval $model_config $model $tmp_src_file $tmp_translate_file --mode beam_search --score_fn $score_file
    
    # export scores of candidate arguments to output file.
    dataPrefix=$expDataDir/knmt
    voc_file=$dataPrefix.voc
    python lookup_export.py --input_file $inputFile --score_file $score_file --output_file $outputFile --voc_file $voc_file --debug

    # cleanup
    rm -f $tmp_translate_file*
    rm -f $tmp_src_file $score_file

elif [ "$type" = "LM" ] ; then
    echo "not supported yet :("
fi

