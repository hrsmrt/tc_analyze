#!/usr/bin/env bash
# nohup sh $WORK/tc_analyze/2d/y_ave.sh &

while read -r line; do
  echo "Processing $line"
  python "${WORK}/tc_analyze/2d/y_ave.py" "$line" "${WORK}/matplotlib/stylesheet/presentation_jp.style"
done < filenames_2d.txt
