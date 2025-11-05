#!/usr/bin/env bash
# nohup sh $WORK/tc_analyze/analyze/2d/whole_domain.sh &

while read -r line; do
  echo "Processing $line"
  python "${WORK}/tc_analyze/analyze/2d/whole_domain.py" "$line" "${WORK}/matplotlib/stylesheet/presentation_jp.style"
done < filenames_2d.txt
