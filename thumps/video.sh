#!/bin/bash
# Generating video
# Written by Yu-Jie Lin in 2016
# Public domain, or via UNLICENSE if not applicable.

opts='-y -loglevel warning -stats'

{
  for i in {1..20}; do ((c = 48 * (i - 1) / 20)); convert -size 1280x720 "canvas:rgb($c,$c,$c)" png24:-; done
} |
ffmpeg \
  $opts \
  -f image2pipe -r 20 -vcodec png -i - \
  -c:v libx264 \
  -r 20 \
  thumps-blank.mp4

{
  for j in {1..4}; do
    n=1; for i in {1..3}; do cat "i$n".png; done
    n=2; for i in {1..6}; do cat "i$n".png; done
    n=3; for i in {1..6}; do cat "i$n".png; done
    n=4; for i in {1..3}; do cat "i$n".png; done
    n=5; for i in {1..20}; do cat "i$n".png; done
  done
} |
ffmpeg \
  $opts \
  -f image2pipe -r 20 -vcodec png -i - \
  -c:v libx264 \
  -r 20 \
  thumps-thumps.mp4

ffmpeg \
  $opts \
  -y \
  -loglevel warning -stats \
  -f concat -i <(echo "file $PWD/thumps-blank.mp4"; echo "file $PWD/thumps-thumps.mp4") \
  -c copy \
  thumps-merged.mp4

ffmpeg \
  $opts \
  -i thumps-merged.mp4 \
  -i thumps.wav \
  -c:v copy \
  -c:a libfdk_aac \
  thumps.mp4
