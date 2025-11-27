#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/azimuthal/basic/azim_2d_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_2d_plot.py $line $style
done < filenames_2d.txt
