#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/vertical/profile/vortex_region_calc.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/vertical/profile/calc/vortex_region_calc.py $line
done < filenames_3d.txt
