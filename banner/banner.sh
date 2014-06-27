#!/bin/bash
# May need to be run using
# $ export COLUMNS LINES ; ./banner.sh

BG_COLOR='#002b36'
TEXT_COLOR='#eee8d5'
IMG_BG='2013-07-30--17:55:25.png'
IMG_TEXT='banner.text.png'
IMG_OVERLAY='banner.overlay.png'
IMG_BANNER='banner.png'
BANNER_SIZE='2048x339'

change-term-font.sh -s 9
win-resize.sh 1024 170 0 18

tput civis
python3 banner.py
xsnap -file "$IMG_TEXT"
IMG_OVERLAY_Y=$((($(identify -format %h "$IMG_BG") - 2 * $(identify -format %h "$IMG_TEXT")) / 2))
read
tput cnorm

convert \
  "$IMG_BG" \
  \( \
    "$IMG_TEXT" \
    -matte \
    -fill none \
    -draw "color 0,0 replace" \
    -resize "$BANNER_SIZE" \
    -repage +0+$IMG_OVERLAY_Y \
  \) \
  -page +8+$((8 + IMG_OVERLAY_Y)) \( \
    +clone \
    -fuzz 50% \
    -fill white \
    -opaque "#TEXT_COLOR" \
  \) \
  -flatten \
  "$IMG_BANNER"

rm -f "$IMG_TEXT" "$IMG_OVERLAY"
