#!/usr/bin/env python

import os
import time

from PIL import Image, ImageDraw, ImageFont
from drawille import Canvas

# https://github.com/python-pillow/Pillow/issues/370
# https://github.com/python-pillow/Pillow/pull/682
FONTPATH = '/usr/share/fonts/inconsolata/Inconsolata.otf'
FONT = ImageFont.truetype(FONTPATH, size=240)
FONT2 = ImageFont.truetype(FONTPATH, size=100)

# The download banner is 2048x339
IM_W = 2048
IM_H = 339

# Not portable and may require
# $ export COLUMNS LINES
TERM_W = int(os.environ.get('COLUMNS', 80))
TERM_H = int(os.environ.get('LINES', 40))

# 2x4 dots of Braille patterns
CANVAS_W = TERM_W * 2
CANVAS_H = TERM_H * 4


def clear(draw):

  draw.rectangle((0, 0, IM_W, IM_H), fill='#000')


def text_READ(draw, x, y):

  clear(draw)
  draw.text((x, y), 'READ', fill='#fff', font=FONT)


def update(im, delay=0.1):

  im = im.resize((CANVAS_W, CANVAS_H))
  canvas = Canvas()
  any(canvas.set(i % CANVAS_W, i // CANVAS_W)
      for i, px in enumerate(im.tobytes()) if px)
  print(canvas.frame(0, 0, CANVAS_W, CANVAS_H))
  time.sleep(delay)


def main():

  im = Image.new('L', (IM_W, IM_H), '#000')
  draw = ImageDraw.Draw(im)
  C_W, C_H = draw.textsize('X', font=FONT)
  C2_W, C2_H = draw.textsize('X', font=FONT2)

  clear(draw)

  TEXT = 'READYT'
  P = ((IM_W - len(TEXT) * C_W) // 2, (IM_H - C_H) // 2)
  draw.text(P, TEXT, fill='#fff', font=FONT)

  TEXT = 'Yu-Jie Lin'
  P = (IM_W - (len(TEXT) + 1) * C2_W, IM_H - C2_H)
  P = (0.5 * C2_W, IM_H - C2_H)
  draw.text(P, TEXT, fill='#fff', font=FONT2)

  update(im, 1.0)


if __name__ == '__main__':
  main()
