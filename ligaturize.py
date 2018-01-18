#!/usr/bin/env python

import fontforge
import os

from ligatures import ligatures

# Constants
SOURCE_FONT_DIR = "input-fonts"
OUTPUT_FONT_DIR = "output-fonts"
COPYRIGHT = '\nProgramming ligatures added by Ilya Skriblovsky from FiraCode\nFiraCode Copyright (c) 2015 by Nikita Prokopov'

def get_input_fontname():
    return raw_input('Enter the source font filename (including extension): ')

def get_input_path(input_fontname):
    return SOURCE_FONT_DIR + "/" + input_fontname

# "RobotoMono-Regular.ttf" -> "RobotoMono-Regular"
def name_without_file_extension(fontname):
    return fontname[:-4] if fontname.endswith(('.otf', '.ttf')) else fontname

# "RobotoMono-Regular" -> "RobotoMono"
def name_without_width_variant(fontname):
    no_variant = fontname
    if fontname.endswith("Regular"):
        no_variant = fontname[:-7]
    elif fontname.endswith("Book"):
        no_variant = fontname[:-4]
    return no_variant[:-1] if (no_variant.endswith(" ") or no_variant.endswith("-")) else no_variant

def get_output_fontname(input_name):
    new_fontname = raw_input('Enter a name for your ligaturized font -- or press ENTER to use the same name: ')
    if new_fontname == "":
        new_fontname = input_name
    return name_without_width_variant(name_without_file_extension(new_fontname))

def get_output_font_details(fontname):
    name_with_spaces = split_camel_case(fontname)
    return {
        'filename': fontname + '.ttf',
        'fontname': fontname,
        'fullname': name_with_spaces,
        'familyname': name_with_spaces,
        'copyright_add': COPYRIGHT,
        'unique_id': name_with_spaces,
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

config = {
    'firacode_ttf': 'FiraCode-Medium.otf',

}

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

input_fontname = get_input_fontname()
input_font_path = get_input_path(input_fontname)

output_fontname = get_output_fontname(input_fontname)
output_font = get_output_font_details(output_fontname)

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
output_full_path = OUTPUT_FONT_DIR + "/" + output_name
font.generate(output_name)
os.rename(output_name, output_full_path)
print "Generated ligaturized font %s in %s" % (output_font['fullname'], output_full_path)
