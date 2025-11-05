#!/bin/bash
# nohup sh $WORK/tc_analyze/azim_mean/azim_2d_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/azim_mean/azim_2d_plot.py $line $style
done < filenames_2d.txt
