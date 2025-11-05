#!/bin/bash
# nohup sh $WORK/tc_analyze/analyze/2d/vortex_region.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/analyze/2d/vortex_region.py $line $WORK/matplotlib/stylesheet/presentation_jp.style
done < filenames_2d.txt
