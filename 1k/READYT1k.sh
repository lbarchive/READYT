#!/bin/bash
# Generating videos
# Written by Yu-Jie Lin in 2016
# Public domain, or via UNLICENSE if not applicable.

if [[ $# != 3 ]]; then
  echo "$0 <thumbs> <audio_file> <output_dir>" >&2
fi

NAME=READYT1k
FILE_OPEN="$3/$NAME-open.mp4"
FILE_MAIN="$3/$NAME-main.mp4"
FILE_FINAL="$3/$NAME.mp4"

LOGLEVEL='-loglevel warning -stats'

FPS=60
AUDIO="$2"
OUTPUT_DIR="$1"

make_open()
{
  {
    P="$OUTPUT_DIR/open"
    for n in {0001..0006}; do
      for i in {1..30}; do cat "$P$n".png; done
    done
  } |
  ffmpeg \
    $LOGLEVEL \
    -f image2pipe -r 30 -vcodec png -i - \
    -f lavfi -i anullsrc \
    -shortest \
    -c:v libx264 \
    -c:a mp3 \
    -r $FPS \
    "$FILE_OPEN"
}

make_main()
{
  {
    P="$OUTPUT_DIR/main"
    for n in {0001..0950}; do cat "$P$n".png; done
    for n in {0951..0971}; do for i in {1..2}; do cat "$P$n".png; done; done
    for n in {0972..0980}; do for i in {1..4}; do cat "$P$n".png; done; done
    for n in {0981..0985}; do for i in {1..6}; do cat "$P$n".png; done; done
    for n in {0986..0994}; do for i in {1..8}; do cat "$P$n".png; done; done
    n=0995; for i in {1..10}; do cat "$P$n".png; done
    n=0996; for i in {1..10}; do cat "$P$n".png; done
    n=0997; for i in {1..13}; do cat "$P$n".png; done
    n=0998; for i in {1..15}; do cat "$P$n".png; done
    n=0999; for i in {1..28}; do cat "$P$n".png; done
    n=1000; for i in {1..30}; do cat "$P$n".png; done

    P="$OUTPUT_DIR/end"
    for n in {0001..0100}; do for i in {1..2}; do cat "$P$n".png; done; done
    n=0100; for i in {1..180}; do cat "$P$n".png; done
  } |
  ffmpeg \
    $LOGLEVEL \
    -f image2pipe -r 30 -vcodec png -i - \
    -i "$AUDIO" \
    -c:v libx264 \
    -c:a copy \
    -r $FPS \
    "$FILE_MAIN"
}

merge()
{
  ffmpeg \
    $LOGLEVEL \
    -f concat -i <(echo "file $FILE_OPEN"; echo "file $FILE_MAIN") \
    -c copy \
    "$FILE_FINAL"
}

rm -f "$FILE_OPEN"
rm -f "$FILE_MAIN"
rm -f "$FILE_FINAL"

make_open
make_main
merge
