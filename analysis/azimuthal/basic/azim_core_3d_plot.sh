#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/azimuthal/basic/azim_core_3d_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/azimuthal/basic/plot/azim_core_3d_plot.py $line $style
done < filenames_3d.txt
