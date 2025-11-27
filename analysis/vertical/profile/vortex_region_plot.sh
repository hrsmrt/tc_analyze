#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/vertical/profile/vortex_region_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/vertical/profile/plot/vortex_region_plot.py $line $style
done < filenames_3d.txt
