#!/usr/bin/env python

import os
import time
from random import random

from drawille import Canvas
from PIL import Image, ImageDraw, ImageFont

# https://github.com/python-pillow/Pillow/issues/370
# https://github.com/python-pillow/Pillow/pull/682
FONTPATH = '/usr/share/fonts/inconsolata/Inconsolata.otf'
FONT = ImageFont.truetype(FONTPATH, size=320)
FONT2 = ImageFont.truetype(FONTPATH, size=96)
FONT3 = ImageFont.truetype(FONTPATH, size=72)

IM_W = 1280
IM_H = 720

# Not portable and may require
# $ export COLUMNS LINES
TERM_W = int(os.environ.get('COLUMNS', 80))
TERM_H = int(os.environ.get('LINES', 24))

# 2x4 dots of Braille patterns
CANVAS_W = TERM_W * 2
CANVAS_H = TERM_H * 4

STEP_X = CANVAS_W / TERM_W
STEP_Y = CANVAS_H / TERM_H


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
  print(canvas.frame(0, 0, CANVAS_W, CANVAS_H), end='')
  time.sleep(delay)


def main():

  im = Image.new('L', (IM_W, IM_H), '#000')
  draw = ImageDraw.Draw(im)
  C_W, C_H = draw.textsize('X', font=FONT)
  C2_W, C2_H = draw.textsize('X', font=FONT2)

  M = 2
  STEPS = int((C_H + (IM_H - C_H) / 2) / STEP_Y / M)
  for i in range(STEPS):
    X_jitter = 5 * STEP_X * random() - 2.5
    y = int(i * STEP_Y * M - C_H)
    text_READ(draw, (IM_W - C_W * 4) // 2 + X_jitter, y)
    update(im)

  M = C2_W / 2
  STEPS = int((IM_W - 0.5 * C2_W) / M / STEP_X) * 2
  Y = (IM_H - C_H) / 2
  for i in range(STEPS):
    X_jitter = 5 * STEP_X * random() - 2.5
    Y_jitter = 5 * STEP_Y * random() - 2.5
    x = (IM_W - 4 * C_W - 2 * C_W * i / STEPS) // 2 + X_jitter
    text_READ(draw, x, Y + Y_jitter)
    P = (IM_W - i * M * STEP_X // 2, Y - (C2_H * 1.5))
    TEXT = 'A CLI lover wants You to'
    draw.text(P, TEXT, fill='#fff', font=FONT2)
    update(im, 0.125)

  M = 50
  STEPS = 10
  for i in range(STEPS):
    F = ImageFont.truetype(FONTPATH, size=320 + M * (STEPS - i))
    CF_W, CF_H = draw.textsize('YT', font=F)
    clear(draw)
    X_jitter = 10 * STEP_X * random() - 5
    Y_jitter = 10 * STEP_Y * random() - 5
    text_READ(draw, (IM_W - 6 * C_W) // 2 + X_jitter, Y + Y_jitter)
    P = (IM_W // 2 + 2 * C_W - CF_W // 2, (IM_H - CF_H) // 2)
    draw.text(P, 'YT', fill='#fff', font=F)
    TEXT = 'A CLI lover wants You to'
    draw.text((0.5 * C2_W, Y - (C2_H * 1.5)), TEXT, fill='#fff', font=FONT2)
    update(im)

  clear(draw)
  draw.text(((IM_W - 6 * C_W) // 2, Y), 'READYT', fill='#fff', font=FONT)
  TEXT = 'A CLI lover wants You to'
  draw.text((0.5 * C2_W, Y - (C2_H * 1.5)), TEXT, fill='#fff', font=FONT2)
  update(im, 1.0)

  draw.text((240, 480), '~1min', fill='#fff', font=FONT2)
  update(im, 1.0)
  draw.text((800, 480), 'music', fill='#fff', font=FONT2)
  update(im, 1.0)
  draw.text((240, 580), 'audio', fill='#fff', font=FONT2)
  update(im, 1.0)

  START = 640
  END = 1220
  TEXT = 'straight to'
  STEPS = len(TEXT)
  draw.ellipse((1220, 670, 1240, 690), fill='#fff')
  update(im, 1.0)
  for i in range(STEPS + 1):
    draw.text((START + C2_W / 2, 580), TEXT[:i], fill='#fff', font=FONT2)
    P = (START, 680, START + i * (END - START) / STEPS, 680)
    draw.line(P, fill='#fff', width=5)
    update(im)
  update(im, 1.0)

  draw.text((C2_W, Y - (C2_H * 0.5)), 'WATCH', fill='#fff', font=FONT3)
  draw.line((780, 490, 1060, 580), fill='#fff', width=5)
  update(im, 0.5)
  TEXT = 'WATCH VIDEO'
  draw.text((C2_W, Y - (C2_H * 0.5)), TEXT, fill='#fff', font=FONT3)
  draw.line((1060, 490, 780, 580), fill='#fff', width=5)
  update(im, 1.0)

  TEXT = 'WATCH VIDEO AND'
  draw.text((C2_W, Y - (C2_H * 0.5)), TEXT, fill='#fff', font=FONT3)
  update(im, 1.0)

  TEXT = 'WATCH VIDEO AND READ'
  draw.text((C2_W, Y - (C2_H * 0.5)), TEXT, fill='#fff', font=FONT3)
  draw.line((220, 590, 500, 680), fill='#fff', width=5)
  update(im, 0.5)
  TEXT = 'WATCH VIDEO AND READ DESCRIPTION'
  draw.text((C2_W, Y - (C2_H * 0.5)), TEXT, fill='#fff', font=FONT3)
  draw.line((500, 590, 220, 680), fill='#fff', width=5)
  update(im, 1.0)


if __name__ == '__main__':
  main()
