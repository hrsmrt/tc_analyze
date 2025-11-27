#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/azimuthal/q8/azim_q8_3d_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/azimuthal/q8/plot/azim_q8_3d_plot.py $line $style
done < filenames_3d.txt
