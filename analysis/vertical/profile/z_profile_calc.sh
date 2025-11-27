#!/bin/bash
# nohup sh $WORK/tc_analyze/analysis/vertical/profile/z_profile_calc.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/vertical/profile/calc/z_profile_calc.py $line
done < filenames_3d.txt
