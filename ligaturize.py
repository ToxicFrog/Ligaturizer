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

from __future__ import print_function

import fontforge
import psMat
import os
from os import path
import sys

from ligatures import ligatures

# Constants
COPYRIGHT = '''
Programming ligatures added by Ilya Skriblovsky from FiraCode
FiraCode Copyright (c) 2015 by Nikita Prokopov'''

def get_ligature_source(fontname):
    for weight in ['Bold', 'Retina', 'Medium', 'Regular', 'Light']:
        if fontname.endswith('-' + weight):
            # Exact match for one of the Fira Code weights
            return 'fira/distr/otf/FiraCode-%s.otf' % weight

    # No exact match. Guess that we want 'Bold' if the font name has 'Bold' in
    # it, and 'Regular' otherwise.
    if 'Bold' in fontname:
        return 'fira/distr/otf/FiraCode-Bold.otf'
    return 'fira/distr/otf/FiraCode-Regular.otf'

class LigatureCreator(object):

    def __init__(self, font, firacode, opts):
        self.font = font
        self.firacode = firacode
        self.opts = opts
        self._lig_counter = 0

        # Scale firacode to correct em height.
        self.firacode.em = self.font.em
        self.emwidth = self.font[ord('m')].width

    def copy_ligature_from_source(self, ligature_name):
        try:
            self.firacode.selection.none()
            self.firacode.selection.select(ligature_name)
            self.firacode.copy()
            return True
        except ValueError:
            return False

    def correct_character_width(self, glyph):
        """Width-correct copied individual characters (not ligatures!).

        This will correct the horizontal advance of characters to match the em
        width of the output font, and (depending on the width of the glyph, the
        em width of the output font, and the value of the command line option
        --scale-character-glyphs-threshold) optionally horizontally scale it.

        Glyphs that are not horizontally scaled, but which still need horizontal
        advance correction, will be centered instead.
        """

        if glyph.width == self.emwidth:
            # No correction needed.
            return

        widthdelta = float(abs(glyph.width - self.emwidth)) / self.emwidth
        if widthdelta >= self.opts.scale_character_glyphs_threshold:
            # Character is too wide/narrow compared to output font; scale it.
            scale = float(self.emwidth) / glyph.width
            glyph.transform(psMat.scale(scale, 1.0))
        else:
            # Do not scale; just center copied characters in their hbox.
            # Fix horizontal advance first, to recalculate the bearings.
            glyph.width = self.emwidth
            # Correct bearings to center the glyph.
            glyph.left_side_bearing = (glyph.left_side_bearing + glyph.right_side_bearing) / 2
            glyph.right_side_bearing = glyph.left_side_bearing

        # Final adjustment of horizontal advance to correct for rounding
        # errors when scaling/centering -- otherwise small errors can result
        # in visible misalignment near the end of long lines.
        glyph.width = self.emwidth


    def copy_character_glyphs(self, chars):
        """Copy individual (non-ligature) characters from the ligature font."""
        if not self.opts.copy_character_glyphs:
            return
        print("Copying %d character glyphs from %s..." % (
            len(chars), self.firacode.fullname))

        for char in chars:
            self.firacode.selection.none()
            self.firacode.selection.select(char)
            self.firacode.copy()
            self.font.selection.none()
            self.font.selection.select(char)
            self.font.paste()
            self.correct_character_width(self.font[char])

    def correct_ligature_width(self, glyph):
        """Correct the horizontal advance and scale of a ligature."""

        if glyph.width == self.emwidth:
            return

        # TODO: some kind of threshold here, similar to the character glyph
        # scale threshold? The largest ligature uses 0.956 of its hbox, so if
        # the target font is within 4% of the source font size, we don't need to
        # resize -- but we may want to adjust the bearings. And we can't just
        # center it, because ligatures are characterized by very large negative
        # left bearings -- they advance 1em, but draw from (-(n-1))em to +1em.
        scale = float(self.emwidth) / glyph.width
        glyph.transform(psMat.scale(scale, 1.0))
        glyph.width = self.emwidth

    def add_ligature(self, input_chars, firacode_ligature_name):
        if firacode_ligature_name is None:
            # No ligature name -- we're just copying a bunch of individual characters.
            self.copy_character_glyphs(input_chars)
            return

        if not self.copy_ligature_from_source(firacode_ligature_name):
            # Ligature not in source font.
            return

        self._lig_counter += 1
        ligature_name = 'lig.{}'.format(self._lig_counter)

        self.font.createChar(-1, ligature_name)
        self.font.selection.none()
        self.font.selection.select(ligature_name)
        self.font.paste()
        self.correct_ligature_width(self.font[ligature_name])

        self.font.selection.none()
        self.font.selection.select('space')
        self.font.copy()

        lookup_name = lambda i: 'lookup.{}.{}'.format(self._lig_counter, i)
        lookup_sub_name = lambda i: 'lookup.sub.{}.{}'.format(self._lig_counter, i)
        cr_name = lambda i: 'CR.{}.{}'.format(self._lig_counter, i)

        for i, char in enumerate(input_chars):
            self.font.addLookup(lookup_name(i), 'gsub_single', (), ())
            self.font.addLookupSubtable(lookup_name(i), lookup_sub_name(i))

            if char not in self.font:
                # We assume here that this is because char is a single letter
                # (e.g. 'w') rather than a character name, and the font we're
                # editing doesn't have glyphnames for letters.
                self.font[ord(char)].glyphname = char

            if i < len(input_chars) - 1:
                self.font.createChar(-1, cr_name(i))
                self.font.selection.none()
                self.font.selection.select(cr_name(i))
                self.font.paste()

                self.font[char].addPosSub(lookup_sub_name(i), cr_name(i))
            else:
                self.font[char].addPosSub(lookup_sub_name(i), ligature_name)

        calt_lookup_name = 'calt.{}'.format(self._lig_counter)
        self.font.addLookup(calt_lookup_name, 'gsub_contextchain', (),
            (('calt', (('DFLT', ('dflt',)),
                       ('arab', ('dflt',)),
                       ('armn', ('dflt',)),
                       ('cyrl', ('SRB ', 'dflt')),
                       ('geor', ('dflt',)),
                       ('grek', ('dflt',)),
                       ('lao ', ('dflt',)),
                       ('latn', ('CAT ', 'ESP ', 'GAL ', 'ISM ', 'KSM ', 'LSM ', 'MOL ', 'NSM ', 'ROM ', 'SKS ', 'SSM ', 'dflt')),
                       ('math', ('dflt',)),
                       ('thai', ('dflt',)))),))
        #print('CALT %s (%s)' % (calt_lookup_name, firacode_ligature_name))
        for i, char in enumerate(input_chars):
            self.add_calt(calt_lookup_name, 'calt.{}.{}'.format(self._lig_counter, i),
                '{prev} | {cur} @<{lookup}> | {next}',
                prev = ' '.join(cr_name(j) for j in range(i)),
                cur = char,
                lookup = lookup_name(i),
                next = ' '.join(input_chars[i+1:]))

        # Add ignore rules
        self.add_calt(calt_lookup_name, 'calt.{}.{}'.format(self._lig_counter, i+1),
            '| {first} | {rest} {last}',
            first = input_chars[0],
            rest = ' '.join(input_chars[1:]),
            last = input_chars[-1])
        self.add_calt(calt_lookup_name, 'calt.{}.{}'.format(self._lig_counter, i+2),
            '{first} | {first} | {rest}',
            first = input_chars[0],
            rest = ' '.join(input_chars[1:]))

    def add_calt(self, calt_name, subtable_name, spec, **kwargs):
        spec = spec.format(**kwargs)
        #print('    %s: %s ' % (subtable_name, spec))
        self.font.addContextualSubtable(calt_name, subtable_name, 'glyph', spec)


def update_font_metadata(font, prefix):
    font.fontname = "%s%s" % (prefix, font.fontname)
    font.fullname = "%s %s" % (prefix, font.fullname)
    font.familyname = "%s %s" % (prefix, font.familyname)
    font.copyright += COPYRIGHT
    font.sfnt_names = tuple(
        (row[0], 'UniqueID', '%s-%s' % (prefix, row[2]))
        if row[1] == 'UniqueID' else row
        for row in font.sfnt_names
    )

def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("input_font_path",
        help="The TTF or OTF font to add ligatures to.")
    parser.add_argument("output_font_path",
        help="The file to save the ligaturized font in.")
    parser.add_argument("--ligature-font-path",
        type=str, default='', metavar='PATH',
        help="The file to copy ligatures from. If unspecified, ligaturize will"
             " attempt to pick a suitable one from fira/distr/otf/ based on the input"
             " font's weight.")
    parser.add_argument("--copy-character-glyphs",
        default=False, action='store_true',
        help="Copy glyphs for (some) individual characters from the ligature"
             " font as well. This will result in punctuation that matches the"
             " ligatures more closely, but may not fit in as well with the rest"
             " of the font.")
    parser.add_argument("--scale-character-glyphs-threshold",
        type=float, default=0.1, metavar='THRESHOLD',
        help="When copying character glyphs, if they differ in width from the"
             " width of the input font by at least this much, scale them"
             " horizontally to match the input font even if this noticeably"
             " changes their aspect ratio. The default (0.1) means to scale if"
             " they are at least 10%% wider or narrower. A value of 0 will scale"
             " all copied character glyphs; a value of 2 effectively disables"
             " character glyph scaling.")
    parser.add_argument("--prefix",
        type=str, default="Liga ",
        help="String to prefix the name of the generated font with.")
    return parser.parse_args()

args = parse_args()

# print('Converting %s to %s using ligatures from %s' % (
#     args.input_font_path, args.output_font_path, args.ligature_font_path))
font = fontforge.open(args.input_font_path)

if args.ligature_font_path:
    ligature_font_path = args.ligature_font_path
else:
    ligature_font_path = get_ligature_source(font.fontname)

print('Reading ligatures from %s' % ligature_font_path)
firacode = fontforge.open(ligature_font_path)

update_font_metadata(font, args.prefix)

creator = LigatureCreator(font, firacode, args)
ligature_length = lambda lig: len(lig['chars'])
for lig_spec in sorted(ligatures, key = ligature_length):
    try:
        creator.add_ligature(lig_spec['chars'], lig_spec['firacode_ligature_name'])
    except Exception as e:
        print('Exception while adding ligature: {}'.format(lig_spec))
        raise

# Work around a bug in Fontforge where the underline height is subtracted from
# the underline width when you call generate().
font.upos += font.uwidth

# Generate font & move to output directory
font.generate(args.output_font_path)
print("Generated ligaturized font %s in %s" % (font.fullname, args.output_font_path))
