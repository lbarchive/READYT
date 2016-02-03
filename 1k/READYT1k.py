#!/usr/bin/env python
# Collecting video thumbnails URLs
# Written by Yu-Jie Lin in 2016
# Public domain, or via UNLICENSE if not applicable.

from __future__ import print_function

import argparse
import json
import logging
import os
import re
import sys
import urllib2
from datetime import datetime as dt
from os import path

import httplib2
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage as BaseStorage
from oauth2client.tools import argparser, run_flow

__project__ = 'READYT1k'
__description__ = 'Collecting video thumbnails URLs'

API_STORAGE = '%s.dat' % __project__
DEFAULT_JSON = '%s.json' % __project__
MAX_RESULTS = 50

W, H = 1920, 1080
FONT_PATH = path.expanduser('~/.fonts/Envy Code R/Envy Code R.ttf')
FONTS = {
  16: ImageFont.truetype(FONT_PATH, 16),
  32: ImageFont.truetype(FONT_PATH, 32),
  128: ImageFont.truetype(FONT_PATH, 128),
}
FILE_BANNER = '../banner/banner.png'
CREDIT = 'Music: For Mimi by Twin Musicom <http://www.twinmusicom.org/> (CC BY 4.0)'

LOGGING_FORMAT = (
  '[%(asctime)s]'
  '[%(levelname)8s]'
  '[%(name)s:%(funcName)s:%(lineno)3d] '
  '%(message)s'
)


class Storage(BaseStorage):
  """Inherit the API Storage to suppress CredentialsFileSymbolicLinkError
  """

  def __init__(self, filename):

    super(Storage, self).__init__(filename)
    self._filename_link_warned = False

  def _validate_file(self):

    if os.path.islink(self._filename) and not self._filename_link_warned:
      print('File: %s is a symbolic link.' % self._filename)
      self._filename_link_warned = True


def auth(filename):

  # JSON from Google Developer Console / Credentials
  with open('READYT1k.secret.json') as f:
    secret = json.load(f)
  FLOW = OAuth2WebServerFlow(
    secret['installed']['client_id'],
    secret['installed']['client_secret'],
    'https://www.googleapis.com/auth/youtube',
    auth_uri='https://accounts.google.com/o/oauth2/auth',
    token_uri='https://accounts.google.com/o/oauth2/token',
  )

  storage = Storage(filename)
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run_flow(FLOW, storage, argparser.parse_args([]))

  http = httplib2.Http()
  return build("youtube", "v3", http=credentials.authorize(http))


def get_upload_playlistId(yt):

  req = yt.channels().list(part='contentDetails', mine=True)
  resp = req.execute()

  return resp['items'][0]['contentDetails']['relatedPlaylists']['uploads']


def process_video(yt, video):

  v_id = video['snippet']['resourceId']['videoId']
  logging.info('processing: %s', v_id)

  # obtain tags and duration and privacy setting
  part = 'id,contentDetails,snippet,status'
  req = yt.videos().list(part=part, id=v_id)
  resp = req.execute()

  v = resp['items'][0]
  s = v['snippet']
  t = s['thumbnails']
  t_opts = ('maxres', 'standard', 'high', 'medium', 'default')
  t_url = list(t[k]['url'] for k in t_opts if k in t)[0]

  logging.info('extracting: %s', s['title'])

  return {
    'id': v_id,
    'snippet': {
      'publishedAt': s['publishedAt'],
      'title': s['title'],
      'thumbnail': t_url,
      'tags': s.get('tags', []),
    },
    'contentDetails': {
      'duration': v['contentDetails']['duration'],
    },
    'status': {
      'privacyStatus': v['status']['privacyStatus'],
    },
  }


def update(yt, data):

  playlistId = data.get('playlistId', None)
  if not playlistId:
    logging.debug('playlistId not in data')
    playlistId = get_upload_playlistId(yt)
    data['playlistId'] = playlistId
  logging.debug('playlistId: %s', playlistId)

  token = None
  # from oldest to newest
  videos = data.get('items', [])
  ids = [v['id'] for v in videos]

  new_videos = []
  req = yt.playlistItems().list(
    part='snippet',
    playlistId=playlistId,
    maxResults=MAX_RESULTS,
    pageToken=token,
  )
  while req:
    resp = req.execute()
    items = resp['items']
    logging.debug('returned videos: %d', len(items))

    for video in items:
      if video['snippet']['resourceId']['videoId'] in ids:
        req = None
        break
      new_videos.append(process_video(yt, video))
    if req:
      req = yt.playlistItems().list_next(req, resp)

  new_videos = sorted(new_videos, key=lambda v: v['snippet']['publishedAt'])
  logging.info('new videos: %d', len(new_videos))

  videos += new_videos
  data['items'] = videos


def filter_videos(videos):

  g = (v for v in videos if v['status']['privacyStatus'] != 'private')
  g = (v for v in g if v['contentDetails']['duration'] != 'PT0S')

  return list(g)


def get_thumb_filename(p, v):

  return path.join(p, '%s.jpg' % v['id'])


def resize_image(im):

  w, h = im.size
  if w == W and h == H:
    return im

  scale = max(1.0 * W / w, 1.0 * H / h)
  new_size = int(scale * w), int(scale * h)
  im = im.resize(new_size, Image.NEAREST)

  x, y = abs(W - new_size[0]) // 2, abs(H - new_size[1]) // 2
  box = (x, y, x + W, y + H)
  im = im.crop(box)

  return im


def render_round_rect(d, r, x1, y1, x2, y2, fill):

  R = 2 * r
  d.rectangle((x1, y1 + r, x2, y2 - r), fill=fill)
  d.rectangle((x1 + r, y1, x2 - r, y2), fill=fill)
  d.ellipse((x1, y1, x1 + R, y1 + R), fill=fill)  # top-left
  d.ellipse((x2 - R, y1, x2, y1 + R), fill=fill)  # top-right
  d.ellipse((x1, y2 - R, x1 + R, y2), fill=fill)  # bottom-left
  d.ellipse((x2 - R, y2 - R, x2, y2), fill=fill)  # bottom-right


def format_time(t):

  d = t / 86400
  t -= d * 86400
  h = t / 3600
  t -= h * 3600
  m = t / 60
  t -= m * 60
  s = t

  text = '%d day%s %2d hour%s %2d minute%s %2d second%s' % (
    d, ' ' if d == 1 else 's',
    h, ' ' if h == 1 else 's',
    m, ' ' if m == 1 else 's',
    s, ' ' if s == 1 else 's',
  )

  return text


def render_frame(im, i, n, v, acc_time, tags):

  im = im.convert('RGBA')
  enc = ImageEnhance.Brightness(im)
  im = enc.enhance(0.5 + 0.5 * (i / n))

  txt = Image.new('RGBA', im.size, (255, 255, 255, 0))
  d = ImageDraw.Draw(txt)

  # render tags

  for j in range(len(tags)):

    font = FONTS[32]
    tag = tags[j][0]
    size = d.textsize(tag, font=font)
    x = 20
    y = 20 + j * 48

    fill = (255, 255, 255, 192)
    r = 8
    render_round_rect(d, r, x - r, y, x + size[0] + r, y + 40, fill)

    fill = (16, 16, 16, 228)
    d.text((x, y), tag, font=font, fill=fill)

  # render text #

  font = FONTS[128]
  size = d.textsize(str(i), font=font)
  x = (W - size[0]) // 2
  y = (H - size[1]) // 2

  fill = (128, 128, 128, 160)
  r = 32
  render_round_rect(d, r, x - r, y, x + size[0] + r, y + size[1] + r, fill)

  fill = (255, 255, 255, 228)
  d.text((x, y), str(i), font=font, fill=fill)

  # render text date

  font = FONTS[32]
  pubdate = v['snippet']['publishedAt'][:10]
  size = d.textsize(pubdate, font=font)
  x = (W - size[0]) // 2
  y = (H - size[1]) // 2 + 128

  fill = (128, 128, 128, 160)
  r = 8
  render_round_rect(d, r, x - r, y, x + size[0] + r, y + size[1] + r, fill)

  fill = (255, 255, 255, 228)
  d.text((x, y), pubdate, font=font, fill=fill)

  # render acc_time

  font = FONTS[32]
  fmt_atime = format_time(acc_time)
  size = d.textsize(fmt_atime, font=font)
  x = (W - size[0]) // 2
  y = (H - size[1]) // 2 + 128 + 64

  fill = (255, 255, 255, 160)
  r = 8
  render_round_rect(d, r, x - r, y, x + size[0] + r, y + 40, fill)

  fill = (32, 32, 32, 228)
  d.text((x, y), fmt_atime, font=font, fill=fill)

  # render progress bar

  bar = Image.new('RGBA', im.size, (255, 255, 255, 0))
  d = ImageDraw.Draw(bar)
  gout = 20
  w_barout = W - 2 * gout
  h_barout = 32
  gin = 4
  w_barin = w_barout - 2 * gin

  fill = (128, 128, 128, 128)
  d.rectangle((gout, H - h_barout - gout, W - gout, H - gout), fill=fill)

  fill = (192, 192, 192, 228)
  w = 1.0 * w_barin * i // n
  p = (gout + gin, H - h_barout - gout + gin, gout + gin + w, H - gout - gin)
  d.rectangle(p, fill=fill)

  # merge into image

  im = Image.alpha_composite(im, txt)
  im = Image.alpha_composite(im, bar)

  return im


def add_tags(tags, new_tags):

  for t in new_tags:
    tags[t] = tags.get(t, 0) + 1


def top_tags(tags, N):

  tags = zip(tags.keys(), tags.values())
  tags = sorted(tags, key=lambda t: t[1], reverse=True)
  return tags[:N]


def main():

  logger = logging.getLogger()

  p = argparse.ArgumentParser(description=__description__)
  p.add_argument('-d', '--debug', action='store_true')
  p.add_argument('-s', '--storage', default=API_STORAGE,
                 help='the credential file (default: %(default)s)')
  p.add_argument('-j', '--json', default=DEFAULT_JSON,
                 help='cached videos in JSON (default: %(default)s)')
  p.add_argument('--auth', action='store_true',
                 help='authorize the script and exit')
  p.add_argument('-u', '--update', action='store_true',
                 help='update the list')
  p.add_argument('-c', '--count', action='store_true',
                 help='count the filtered list')
  p.add_argument('-D', '--download', type=str, metavar='DIR',
                 help='download thumbnails of videos from the filtered list')
  p.add_argument('-g', '--generate', type=str, metavar='DIR',
                 help='download thumbnails of videos from the filtered list')
  args = p.parse_args()

  logging.basicConfig(format=LOGGING_FORMAT)
  if args.debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

  if args.auth or args.update:
    yt = auth(args.storage)
    if args.auth:
      return

  data = {}
  if path.exists(args.json):
    with open(args.json) as f:
      data = json.load(f)
    logging.debug('%s loaded' % args.json)

  if args.update:
    update(yt, data)
    with open(args.json, 'w') as f:
      json.dump(data, f)
  videos = data.get('items', [])
  logging.info('total videos: %d', len(videos))

  if args.count or args.download or args.generate:
    videos = filter_videos(videos)
    logging.info('filtered videos: %d', len(videos))

    if args.download:
      if not path.exists(args.download):
        os.makedirs(args.download)

      for v in videos:
        filename = get_thumb_filename(args.download, v)
        if path.exists(filename):
          continue
        thumb = v['snippet']['thumbnail']
        logging.info('downloading %s' % thumb)
        uf = None
        try:
          uf = urllib2.urlopen(thumb)
          with open(filename, 'wb') as f:
            f.write(uf.read())
          logging.info('saved: %s' % filename)
        except Exception as e:
          raise e
        finally:
          if uf:
            uf.close()

    if args.generate:
      if not args.download:
        logging.error('--download is required')
        sys.exit(1)
      if not path.exists(args.generate):
        os.makedirs(args.generate)

      t_open = resize_image(Image.open('READYT1k.png')).convert('RGBA')

      # rending opening frames

      filename = path.join(args.generate, 'open%04d.png' % 1)
      logging.debug('saving frame: %s' % filename)
      t_open.save(filename)

      dots = 5
      for i in range(dots):
        t = t_open.copy()
        d = ImageDraw.Draw(t)
        x = W // 2
        y = H - H // 4
        r = 40
        D = 180
        fill = (192, 192, 192, 64)
        for j in range(dots - i):
          p = (x - r + (j - 2) * D, y - r, x + r + (j - 2) * D, y + r)
          d.ellipse(p, fill=fill)

        filename = path.join(args.generate, 'open%04d.png' % (i + 2))
        logging.debug('saving frame: %s' % filename)
        t.save(filename)

      # render main frames

      # n = len(videos)
      n = 1000
      acc_time = 0
      tags = {}
      RE_T = re.compile('PT((?P<m>\d+)M)?((?P<s>\d+)S)?')
      for i in range(n):
        if i < len(videos):
          v = videos[i]
        else:
          v = {
            'contentDetails': {
              'duration': 'PT1M3S',
            },
            'snippet': {
              'publishedAt': '2016-02-03',
              'tags': [
                'test',
              ],
            },
          }
        m = RE_T.match(v['contentDetails']['duration'])
        acc_time += int(m.group('m') or 0) * 60 + int(m.group('s') or 0)
        add_tags(tags, v['snippet']['tags'])

        if 'id' in v:
          t = Image.open(get_thumb_filename(args.download, v))
        else:
          t = Image.new('RGBA', (W, H), (255, 255, 255, 0))
        t = resize_image(t)
        t = render_frame(t, i + 1, n, v, acc_time, top_tags(tags, 20))

        filename = path.join(args.generate, 'main%04d.png' % (i + 1))
        logging.debug('saving frame: %s' % filename)
        t.save(filename)

      drange = (
        videos[0]['snippet']['publishedAt'][:10],
        videos[n - 1]['snippet']['publishedAt'][:10],
      )
      dfmt = '%Y-%m-%d'
      ddiff = dt.strptime(drange[1], dfmt) - dt.strptime(drange[0], dfmt)
      fmt = 'published date range: %s to %s (%d days)'
      logging.info(fmt % (drange[0], drange[1], ddiff.days))
      logging.info('accumulated runtime: %s' % format_time(acc_time))
      total_tags = sum(tags.values())
      avg_tags = total_tags / n
      logging.info('total tags: %d (avg. %d/video)' % (total_tags, avg_tags))
      for i, tag in enumerate(top_tags(tags, 5)):
        logging.info('#%d tag: %s (%d)' % (i + 1, tag[0], tag[1]))

      # render ending frames

      t_banner = resize_image(Image.open(FILE_BANNER)).convert('RGBA')
      last_t = t

      # add audio credit
      d = ImageDraw.Draw(t_banner)
      size = d.textsize(CREDIT, font=FONTS[32])
      x, y = (W - size[0] - 20, H - size[1] - 20)
      fill = (128, 128, 128, 160)
      r = 8
      render_round_rect(d, r, x - r / 2, y, x + size[0], y + size[1] + r / 4, fill)
      fill = (255, 255, 255, 228)
      d.text((x, y), CREDIT, font=FONTS[32], fill=fill)

      end_frames = 100 - 1
      for i in range(end_frames + 1):
        t = Image.blend(last_t, t_banner, 1.0 * i / end_frames)

        filename = path.join(args.generate, 'end%04d.png' % (i + 1))
        logging.debug('saving frame: %s' % filename)
        t.save(filename)


if __name__ == '__main__':
  main()
