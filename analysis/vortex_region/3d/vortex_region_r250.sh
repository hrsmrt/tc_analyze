#!/bin/bash

# nohup sh $WORK/tc_analyze/analysis/vortex_region/3d/vortex_region_r250.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analysis/vortex_region/3d/plot/vortex_region_r250.py $line $WORK/matplotlib/stylesheet/presentation_jp.style
done < filenames_3d.txt
