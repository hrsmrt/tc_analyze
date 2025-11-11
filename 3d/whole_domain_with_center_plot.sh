#!/usr/bin/env bash
# nohup sh $WORK/tc_analyze/3d/whole_domain_with_center_plot.sh &

while read -r line; do
  echo "Processing $line"
  python "${WORK}/tc_analyze/3d/whole_domain_with_center_plot.py" "$line" "${WORK}/matplotlib/stylesheet/presentation_jp.style"
done < filenames_3d.txt
