#!/bin/bash

# nohup sh $WORK/tc_analyze/3d/vortex_region.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/3d/vortex_region.py $line $WORK/matplotlib/stylesheet/presentation_jp.style
done < filenames_3d.txt
