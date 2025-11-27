#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/diagnostics/sums/sums_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/diagnostics/sums/plot/sums_plot.py $line $style
done < filenames_3d.txt
