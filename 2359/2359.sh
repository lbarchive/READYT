#!/bin/bash
# Generating 23:59 video
# Written in 2017 by Yu-Jie Lin
# UNLICENSE has been applied to this script

if [[ $# > 1 ]]; then
  echo "$0 <output_dir>" >&2
  exit 1
fi

NAME=2359
OUTPUT_DIR="${1:-/tmp}"
FILE_2359="$OUTPUT_DIR/$NAME.mp4"

LOGLEVEL='-loglevel warning -stats'

FPS=30

make_2359()
{
  {
    P=0
    n=1800
    while ((n > 0)); do
      ((j = 60 - (1800 - n) / 30))
      ((j > 55)) && j=0 || ((j = 60 - j))
      for ((i = 0; i < 30 + j; i++)); do
        cat "CLOCK$P".png;
        ((n--))
        ((n <= 0)) && break 2
      done
      ((P = (P + 1) % 2))
    done
  } |
  ffmpeg \
    $LOGLEVEL \
    -f image2pipe -r 30 -vcodec png -i - \
    -c:v libx264 \
    -r $FPS \
    "$FILE_2359"
}

rm -f "$FILE_2359"

make_2359
