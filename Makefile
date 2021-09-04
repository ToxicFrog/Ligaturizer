# To build with different settings (e.g. turn on character glyph copying),
# edit build.py and then "make".

all:
	fontforge -lang=py -script build.py 2>&1 \
	| grep -Fv 'This contextual rule applies no lookups.' \
	| grep -Fv 'Bad device table'
