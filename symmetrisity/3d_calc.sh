#!/bin/bash
# nohup sh $WORK/tc_analyze/symmetrisity/3d_calc.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/symmetrisity/3d_calc.py $line
done < filenames_3d.txt
