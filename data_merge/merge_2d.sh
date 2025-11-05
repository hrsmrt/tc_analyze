#!/bin/bash
# nohup sh $WORK/tc_analyze/data_merge/merge_2d.sh &

while read line; do
  echo "Processing $line"
  python $WORK/tc_analyze/data_merge/merge_2d.py $line
done < filenames_2d.txt
