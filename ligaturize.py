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

from ligatures import ligatures

# Constants
COPYRIGHT = '''
Programming ligatures added by Ilya Skriblovsky from FiraCode
FiraCode Copyright (c) 2015 by Nikita Prokopov'''

def get_ligature_source(fontname):
    if len(sys.argv) > 3:
        # User explicitly told us which source to use.
        return sys.argv[3]

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

    def __init__(self, font, firacode):
        self.font = font
        self.firacode = firacode

        self._lig_counter = 0

    def copy_ligature_from_source(self, ligature_name):
        try:
            self.firacode.selection.none()
            self.firacode.selection.select(ligature_name)
            self.firacode.copy()
            return True
        except ValueError:
            return False

    def add_ligature(self, input_chars, firacode_ligature_name):
        if firacode_ligature_name is None:
            # No ligature name -- we're just copying a bunch of individual characters.
            for char in input_chars:
                self.firacode.selection.none()
                self.firacode.selection.select(char)
                self.firacode.copy()
                self.font.selection.none()
                self.font.selection.select(char)
                self.font.paste()
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

input_font_path = sys.argv[1]
output_font_path = sys.argv[2]

output_font = get_output_font_details(output_font_path)

font = fontforge.open(input_font_path)
ligature_font_path = get_ligature_source(output_font['fontname'])
print('Reading ligatures from %s' % ligature_font_path)
firacode = fontforge.open(ligature_font_path)
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

# Work around a bug in Fontforge where the underline height is subtracted from
# the underline width when you call generate().
font.upos += font.uwidth

# Generate font & move to output directory
output_name = output_font['filename']
font.generate(output_font_path)
print "Generated ligaturized font %s in %s" % (output_font['fullname'], output_font_path)
