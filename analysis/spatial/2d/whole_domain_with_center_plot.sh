#!/usr/bin/env bash
# nohup sh $WORK/tc_analyze/analysis/spatial/2d/whole_domain_with_center_plot.sh &

while read -r line; do
  echo "Processing $line"
  python "${WORK}/tc_analyze/analysis/spatial/2d/plot/whole_domain_with_center_plot.py" "$line" "${WORK}/matplotlib/stylesheet/presentation_jp.style"
done < filenames_2d.txt
