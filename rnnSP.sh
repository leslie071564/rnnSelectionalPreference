#!/bin/bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
make_sample_script=$SCRIPTPATH/make_sample/make_sample.sh
prepare_train_script=$SCRIPTPATH/prepare_train/prepare_train.sh
evaluate_script=$SCRIPTPATH/evaluate/evaluate.sh

case $1 in
    "make_sample")
        $make_sample_script "${@:2}";
        ;;
    "prepare_train")
        $prepare_train_script "${@:2}";
        ;;
    "eval")
        $evaluate_script "${@:2}";
        ;;
    *)
        echo "invalid input-mode"
        ;;
esac
