#!/usr/bin/env bash

# Ensure to have ImageMagick installed

in_file=$1
out_file=$2

# Results in 980x980 pixels image with transparent background without skewing the original logo
convert ${in_file} -trim +repage -resize 980x980 -gravity center -background transparent -extent 980x980 ${out_file}

# Add a default border of 10 pixels
convert ${out_file} -bordercolor transparent -border 10 ${out_file}
