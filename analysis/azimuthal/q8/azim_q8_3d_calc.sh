#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/azimuthal/q8/azim_q8_3d_calc.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/azimuthal/q8/calc/azim_q8_3d_calc.py $line
done < filenames_3d.txt
