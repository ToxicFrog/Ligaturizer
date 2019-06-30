#!/usr/bin/env python
#
# usage: fontforge -lang=py ligaturize.py <input file> <output file> [ligature file]
#
# It will copy input to output, updating the embedded font name and splicing
# in the ligatures from FiraCode-Medium.otf (which must be in $PWD). If the
# ligature file is not specified, it will try to guess an appropriate Fira Code
# OTF based on the name of the output file.
#
# See ligatures.py for a list of all the ligatures that will be copied.

import fontforge
import os
from os import path
import sys

input_font_path = sys.argv[1]
font = fontforge.open(input_font_path)

for field in dir(font):
  if field.startswith('__'):
    continue
  value = getattr(font, field)
  if 'built-in' in str(value):
    continue
  print("%s = %s" % (field, value))
#print "emwidth = %d" % (font['m'].width)
print("emwidth = %d" % (font[ord('m')].width))
print("aspect = %f" % (float(font[ord('m')].width)/font.em))

#print "font: %d %d %d " % (font.upos, font.capHeight, font.xHeight)

