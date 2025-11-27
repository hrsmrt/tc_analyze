#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/diagnostics/symmetrisity/3d_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/diagnostics/symmetrisity/plot/3d_plot.py $line $style
done < filenames_3d.txt
