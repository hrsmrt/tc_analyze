#!/bin/bash
# nohup sh $WORK/tc_analyze/z_profile/z_profile_plot.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/z_profile/z_profile_plot.py $line $style
done < filenames_3d.txt
