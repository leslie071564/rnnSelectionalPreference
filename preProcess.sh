#!/bin/sh
fileID="$1"
config="$2"
NICE="nice -n 19"

### process config file.
type=`cat $config | shyaml get-value ExpSetting.sampleType`
rawPrefix=`cat $config | shyaml get-value ExpLocation.PreProcess.RawPrefix`
tmpPrefix=`cat $config | shyaml get-value ExpLocation.PreProcess.TempPrefix`
pcdPrefix=`cat $config | shyaml get-value ExpLocation.PreProcess.ProcessedPrefix`

rawFile=$rawPrefix$fileID
tmpFile=$tmpPrefix$fileID.txt
pcdFile=$pcdPrefix$fileID.txt


### exatrct training samples.
preProcessScript=`cat $config | shyaml get-value Scripts.preProcessScript`
$NICE python $preProcessScript --config $config --output_file $tmpFile --input_file $rawFile

if [ "$type" = "MT" ] ; then
    # locally uniq
    $NICE sort -u -o $tmpFile $tmpFile
    # print to file
    cp $tmpFile $pcdFile

elif [ "$type" = "LM" ] ; then
    # locally uniq
    $NICE sort -u -o $tmpFile $tmpFile
    # print to file
    cp $tmpFile $pcdFile

elif [ "$type" = "REP" ] ; then
    # merge
    LC_ALL=C sort -t'#' -k1,1 -o $tmpFile $tmpFile
    $NICE python $preProcessScript --merge_file --config $config --input_file $tmpFile --output_file $pcdFile
fi

#rm $tmpFile
echo $fileID done
