#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/diagnostics/sums/sums_calc.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/diagnostics/sums/calc/sums_calc.py $line
done < filenames_3d.txt
