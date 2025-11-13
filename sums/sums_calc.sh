#!/bin/bash
# nohup sh $WORK/tc_analyze/sums/sums_calc.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/sums/sums_calc.py $line
done < filenames_3d.txt
