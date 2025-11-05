#!/bin/bash

while read line; do
  echo "Processing $line"
  python $WORK/p-nicam/analyze/mkfig/2d/2d.py $line
done < filenames_2d.txt
