#!/bin/bash
# nohup sh $WORK/tc_analyze/azim_q8/azim_q8_3d_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/azim_q8/azim_q8_3d_plot.py $line $style
done < filenames_3d.txt
