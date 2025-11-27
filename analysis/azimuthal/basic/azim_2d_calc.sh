#!/bin/bash
# nohup sh $WORK/tc_analyze/azim_mean/azim_2d_calc.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/azim_mean/azim_2d_calc.py $line
done < filenames_2d.txt
