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
            return 'fira/FiraCode-%s.otf' % weight

    # No exact match. Guess that we want 'Bold' if the font name has 'Bold' in
    # it, and 'Regular' otherwise.
    if 'Bold' in fontname:
        return 'fira/FiraCode-Bold.otf'
    return 'fira/FiraCode-Regular.otf'

def get_output_font_details(fontpath):
    fontname = path.splitext(path.basename(fontpath))[0]
    if '-' in fontname:
        [family, weight] = fontname.split('-', 1)
    else:
        [family, weight] = [fontname, 'Regular']
    return {
        'filename': fontpath,
        'fontname': '%s-%s' % (family, weight),
        'fullname': '%s %s' % (split_camel_case(family), split_camel_case(weight)),
        'familyname': family,
        'copyright_add': COPYRIGHT,
        'unique_id': '%s-%s' % (family, weight),
    }

# Add spaces to UpperCamelCase: 'DVCode' -> 'DV Code'
def split_camel_case(str):
    acc = ''
    for (i, ch) in enumerate(str):
        prevIsSpace = i > 0 and acc[-1] == ' '
        nextIsLower = i + 1 < len(str) and str[i + 1].islower()
        isLast = i + 1 == len(str)
        if i != 0 and ch.isupper() and (nextIsLower or isLast) and not prevIsSpace:
            acc += ' ' + ch
        elif ch == '-' or ch == '_' or ch == '.':
            acc += ' '
        else:
            acc += ch
    return acc


class LigatureCreator(object):

    def __init__(self, font, firacode, opts):
        self.font = font
        self.firacode = firacode
        self.opts = opts
        self._lig_counter = 0

        # Scale firacode to correct em height.
        self.firacode.em = self.font.em
        self.emwidth = self.font['m'].width

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

        self.font.selection.none()
        self.font.selection.select('space')
        self.font.copy()

        lookup_name = lambda i: 'lookup.{}.{}'.format(self._lig_counter, i)
        lookup_sub_name = lambda i: 'lookup.sub.{}.{}'.format(self._lig_counter, i)
        cr_name = lambda i: 'CR.{}.{}'.format(self._lig_counter, i)

        for i, char in enumerate(input_chars):
            self.font.addLookup(lookup_name(i), 'gsub_single', (), ())
            self.font.addLookupSubtable(lookup_name(i), lookup_sub_name(i))

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



def change_font_names(font, fontname, fullname, familyname, copyright_add, unique_id):
    font.fontname = fontname
    font.fullname = fullname
    font.familyname = familyname
    font.copyright += copyright_add
    font.sfnt_names = tuple(
        (row[0], 'UniqueID', unique_id) if row[1] == 'UniqueID' else row
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
             " attempt to pick a suitable one from fira/ based on the input"
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
    return parser.parse_args()

args = parse_args()

output_font = get_output_font_details(args.output_font_path)
font = fontforge.open(args.input_font_path)

if args.ligature_font_path:
    ligature_font_path = args.ligature_font_path
else:
    ligature_font_path = get_ligature_source(output_font['fontname'])

print('Reading ligatures from %s' % ligature_font_path)
firacode = fontforge.open(ligature_font_path)

creator = LigatureCreator(font, firacode, args)
ligature_length = lambda lig: len(lig['chars'])
for lig_spec in sorted(ligatures, key = ligature_length):
    try:
        creator.add_ligature(lig_spec['chars'], lig_spec['firacode_ligature_name'])
    except Exception as e:
        print('Exception while adding ligature: {}'.format(lig_spec))
        raise

change_font_names(font, output_font['fontname'],
                        output_font['fullname'],
                        output_font['familyname'],
                        output_font['copyright_add'],
                        output_font['unique_id'])

# Work around a bug in Fontforge where the underline height is subtracted from
# the underline width when you call generate().
font.upos += font.uwidth

# Generate font & move to output directory
output_name = output_font['filename']
font.generate(args.output_font_path)
print "Generated ligaturized font %s in %s" % (output_font['fullname'], args.output_font_path)
