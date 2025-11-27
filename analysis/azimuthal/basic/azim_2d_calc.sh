#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/azimuthal/basic/azim_2d_calc.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/azimuthal/basic/calc/azim_2d_calc.py $line
done < filenames_2d.txt
