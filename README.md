# Ligaturizer #

![](images/banner.png)

**Add ligatures to any coding font!**

This script copies the ligatures (glyphs and rendering information) from [Fira Code](https://github.com/tonsky/FiraCode) into any other TrueType or OpenType font. (Note that the ligatures are scale-corrected, but otherwise copied as is from Fira Code; it doesn't create new ligature graphics based on the font you're modifying.)

This repo contains a [Fontforge python script](ligaturize.py) that you can use to add the Fira Code ligatures to any font, as well as submodules for some popular coding fonts and [another script](build.py) for ligaturizing all of them at once.

Pre-ligaturized versions are available under [releases](https://github.com/ToxicFrog/Ligaturizer/releases).

Here's a couple examples of the fonts generated: SF Mono & Menlo with ligatures (note the `!=` and `->`):
![](images/sf-mono.png)
![](images/menlo.png)

## Requirements ##
**This Repo**: You'll need the repo and its submodules, so `git clone` with `--recurse-submodules`.

**Using the Fonts**: See the [FiraCode README](https://github.com/tonsky/FiraCode) for a list of supported editors.

**Script**: This script requires FontForge python bindings. For Debian/Ubuntu they are available in `python-fontforge` package. For OpenSUSE and NixOS, they are included in the `fontforge` package. For macOS, they are available via brew (`brew install fontforge`).

## Using the Script ##
### Automatic ###

Use automatic mode to easily convert 1 or more font(s).

1.  Put the font(s) you want into `fonts/`.
1.  Edit `ligatures.py` to disable any ligatures you don't want, and/or enable any (non-ligature) characters you want from Fira Code in addition to the ligatures.
1.  Edit `build.py` to add your new font(s) to the `prefixed_fonts` list. It supports globbing, so if (e.g.) you want to ligaturize all the different weights of FooFont you can add `'FooFont*'` to the list.
1.  Run `make`.
1.  Retrieve the ligaturized fonts from `fonts/output/`.
1.  The output fonts will be renamed with the prefix "Liga".

### Manual ###

1.  Move/copy the font you want to ligaturize into `fonts/` (or somewhere else convenient).
1.  Edit `ligatures.py` to disable any ligatures you don't want.
1.  Run the script:

    ```
    $ fontforge -lang py -script ligaturize.py path/to/input/font.ttf
        --output-dir=path/to/output/dir/ \
        --output-name='Name of Ligaturized Font'
    ```
    e.g.

    ```
    $ fontforge -lang py -script ligaturize.py fonts/Cousine-Regular.ttf
        --output-dir='fonts/output/' \
        --output-name='Ligaturized Cousine'
    ```

    Which will produce `fonts/output/LigaturizedCousine-Regular.ttf`.

The font weight will be inherited from the original file; the font name will be replaced with whatever you specified in `--output-name`. You can also use `--prefix` instead, in which case the original name will be preserved and whatever you put in `--prefix` will be prepended to it.

`ligatures.py` supports some additional command line options to (e.g.) change which font ligatures are copied from or enable copying of individual character glyphs; run `fontforge -lang=py ligaturize.py --help` to list them.

## Misc. ##
### Credit ###
This script was originally written by [IlyaSkriblovsky](https://github.com/IlyaSkriblovsky) for adding ligatures to DejaVuSans Mono ([dv-code-font](https://github.com/IlyaSkriblovsky/dv-code-font)). [Navid Rojiani](https://github.com/rojiani) made a few changes to generalize the script so that it works for any font. [ToxicFrog](https://github.com/ToxicFrog) has made a large number of contributions.

### Contributions ###
Contributions always welcome! Please submit a Pull Request, or create an Issue if you have an idea for a feature/enhancement (or bug).

### Related Projects ###
For more awesome programming fonts with ligatures, check out:
1. [FiraCode](https://github.com/tonsky/FiraCode)
2. [Hasklig](https://github.com/i-tu/Hasklig)
