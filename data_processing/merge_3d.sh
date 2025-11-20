#!/bin/bash
# nohup sh $WORK/tc_analyze/data_merge/merge_3d.sh &

while read line; do
  echo $(date)
  echo "Processing $line"
  python $WORK/tc_analyze/data_merge/merge_3d.py $line
  echo $(date)
done < filenames_3d.txt
