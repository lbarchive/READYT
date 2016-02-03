=========
READYT/1k
=========

.. figure:: READYT1k.png
  :target: video_

  |j|__

.. _video: https://youtu.be/dAlnoh_Kp8I
.. |j| replace:: *The Journey of READYT's 1,000 Videos*
__ video_

**READYT/1k** is a one-time project for READYT_. It's a set of scripts and assets for generating a 1080p60 video for 1,000 videos of the `YouTube channel`_.

.. _READYT: ..
.. _YouTube channel: https://www.youtube.com/channel/UCYgk0h0P55kxFgNLF6E-uKA


.. contents:: **Contents**
   :local:


The video
=========

There is three parts:

1. the opening scene, which doesn't reveal what this video is about yet.
2. the main scene, the fast-paced slideshow of 1,000 video thumbnails:

   Each thumbnail of video is displayed in background with

   1. the video number at center as the focal point,
   2. the published date just below the number,
   3. the accumulated runtime of the videos up to the currently shown video thumbnail,
   4. the progress bar at bottom, for 1 to 1,000, and lastly
   5. the top tags up to the current thumbnail.

3. the ending scene, the READYT 2016/new banner fading in.


Notes
=====

1. Originally, one thumbnail per frame @ 30 fps and 1,000 frames in total, but I decided to double the rate to 60fps for 1080p60, that is 2 frames @ 60 fps for every thumbnail.
2. The original idea for progress bar was to use ASCII like ``###>``, but I drew a graphical one first and have used it since.
3. 13 videos are not included: Private and 0-second length (encoding failure and a live stream video) video.
4. The code isn't in good quality.
5. After this video, the channel has been renamed to "Yu-Jie Lin."


Dependencies
============

* Python
* Google's `API Client Library for Python`_
* Pillow
* Bash
* FFmpeg

.. _`API Client Library for Python`: https://developers.google.com/api-client-library/python/


Usage
=====

It's meant for me and one-time use only.

Here are the steps:

1. Create an project with YouTube Data API v3 enabled, create an credential, then download the credential JSON and save as ``READYT1k.secret.json``.

2. ``REATYT1k.py`` gets thumbnails and generates frames:

   .. code:: bash

     # -d debug messages
     # -u update JSON list
     # -D download thumbnails to /tmp/thumbs
     # -g generate frames to /tmp/frames

     % ./READYT1k.py -d -u -D /tmp/thumbs -g /tmp/frames

3. ``REATYT1k.sh`` produces videos:

   .. code:: bash

     # ./READYT1k.sh <frames> <audio_file> <output_dir>
     % ./READYT1k.sh /tmp/frames For_Mimi.mp3 /tmp

   There should be three files at ``/tmp``:

   a. ``REATYT1k-open.mp4``: opening scene with dummy audio
   b. ``REATYT1k-main.mp4``: main and ending scene with audio
   c. ``REATYT1k.mp4`` is the final video.


Assets
======

1. |READYT1k.png|_: the opening frame
2. |banner.png|_: the ending frame
3. |For_Mimi.mp3|:

   It can be downloaded from YouTube Audio Library, and the credit is:

     For Mimi by Twin Musicom is licensed under a Creative Commons Attribution license (https://creativecommons.org/licenses/by/4.0/)
     Artist: http://www.twinmusicom.org/ 

4. `Envy Code R`_ Preview 7.2 font by Damien Guard

     Copyright © 2006-2008 Envy Technologies Ltd.  Free to use but redistribution prohibited.

.. |READYT1k.png| replace:: ``READYT1k.png``
.. _READYT1k.png: READYT1k.png
.. |banner.png| replace:: ``banner.png``
.. _banner.png: ../banner/banner.png
.. |For_Mimi.mp3| replace:: ``For_Mimi.mp3``
.. _Envy Code R: https://damieng.com/blog/tag/envy-code-r


Copyright
=========

Like READYT, this project has been placed into public domain, or via UNLICENSE_, if not applicable.

.. _UNLICENSE: ../UNLICENSE
