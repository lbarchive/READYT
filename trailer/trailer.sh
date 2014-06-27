#!/bin/bash
# May need to be run using
# $ export COLUMNS LINES ; ./trailer.sh

change-term-font.sh -s 9
win-resize.sh 1280 720 0 18

tput civis
clear
sleep 3
python3 trailer.py
read
tput cnorm

# after recording,
# $ ffmpeg -i input.mkv -pix_fmt rgb24 -r 5 trailer.input.gif
# $ gifsicle -O3 trailer.input.gif > trailer.gif
