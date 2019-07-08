#!bin/bash

runs=(297485 297488 297505 297562 297603 297674 297723 299000 297467 297483 297486 297503 297557 297563 297666 297675 298996 299042 )


for run_num in ${runs[@]}; do
    echo copying $run_num
    mv run$run_num/$run_num /hadoop/users/ndev/DQM_ML/good_2017/
    rm -rf run$run_num
done
