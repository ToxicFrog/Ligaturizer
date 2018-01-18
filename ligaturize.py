#!/usr/bin/env python
#
# usage: fontforge -lang=py ligaturize.py <input file> <output file>
#
# It will copy input to output, updating the embedded font name and splicing
# in the ligatures from FiraCode-Medium.otf (which must be in $PWD).
#
# See ligatures.py for a list of all the ligatures that will be copied.

import fontforge
import os
from os import path
import sys

from ligatures import ligatures

# Constants
COPYRIGHT = '''
Programming ligatures added by Ilya Skriblovsky from FiraCode
FiraCode Copyright (c) 2015 by Nikita Prokopov'''

config = {
    'firacode_ttf': 'FiraCode-Medium.otf',
}

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

    def __init__(self, font, firacode):
        self.font = font
        self.firacode = firacode

        self._lig_counter = 0

    def add_ligature(self, input_chars, firacode_ligature_name):
        self._lig_counter += 1

        ligature_name = 'lig.{}'.format(self._lig_counter)

        self.font.createChar(-1, ligature_name)
        firacode.selection.none()
        firacode.selection.select(firacode_ligature_name)
        firacode.copy()
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
        self.font.addLookup(calt_lookup_name, 'gsub_contextchain', (), (('calt', (('DFLT', ('dflt',)), ('arab', ('dflt',)), ('armn', ('dflt',)), ('cyrl', ('SRB ', 'dflt')), ('geor', ('dflt',)), ('grek', ('dflt',)), ('lao ', ('dflt',)), ('latn', ('CAT ', 'ESP ', 'GAL ', 'ISM ', 'KSM ', 'LSM ', 'MOL ', 'NSM ', 'ROM ', 'SKS ', 'SSM ', 'dflt')), ('math', ('dflt',)), ('thai', ('dflt',)))),))
        for i, char in enumerate(input_chars):
            ctx_subtable_name = 'calt.{}.{}'.format(self._lig_counter, i)
            ctx_spec = '{prev} | {cur} @<{lookup}> | {next}'.format(
                prev = ' '.join(cr_name(j) for j in range(i)),
                cur = char,
                lookup = lookup_name(i),
                next = ' '.join(input_chars[i+1:]),
            )
            self.font.addContextualSubtable(calt_lookup_name, ctx_subtable_name, 'glyph', ctx_spec)


def change_font_names(font, fontname, fullname, familyname, copyright_add, unique_id):
    font.fontname = fontname
    font.fullname = fullname
    font.familyname = familyname
    font.copyright += copyright_add
    font.sfnt_names = tuple(
        (row[0], 'UniqueID', unique_id) if row[1] == 'UniqueID' else row
        for row in font.sfnt_names
    )

input_font_path = sys.argv[1]
output_font_path = sys.argv[2]

output_font = get_output_font_details(output_font_path)

font = fontforge.open(input_font_path)
firacode = fontforge.open(config['firacode_ttf'])
firacode.em = font.em

creator = LigatureCreator(font, firacode)
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


# Generate font & move to output directory
output_name = output_font['filename']
font.generate(output_name)
os.rename(output_name, output_font_path)
print "Generated ligaturized font %s in %s" % (output_font['fullname'], output_font_path)
