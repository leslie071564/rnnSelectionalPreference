#!/bin/bash

case $1 in
    "make_sample")
        ./make_sample.sh "${@:2}"; 
        ;;
    "prepare_train")
        ./prepare_train.sh "${@:2}";
        ;;
    "eval")
        ./generate_result.sh "${@:2}"
        ;;
    "lookup")
        ./lookup.sh "${@:2}"
        ;;
    *)
        echo invalid
        ;;
esac
