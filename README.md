# Ligaturizer #

![](images/banner.png)

**Add ligatures to any coding font!**

This script copies the ligatures (glyphs and rendering information) from [Fira Code](https://github.com/tonsky/FiraCode) into any other TrueType or OpenType font. (Note that the ligatures are scale-corrected, but otherwise copied as is from Fira Code; it doesn't create new ligature graphics based on the font you're modifying.)

**This repo contains 2 things:**

1.  Programming fonts with ligatures added (in `output-fonts/`), including:
    * [Anonymous Pro](output-fonts/LigaAnonymous_Pro.ttf)  
    * [CamingoCode](output-fonts/LigaCamingoCode-Regular.ttf)  
    * Cousine: [Regular](output-fonts/LigaCousine-Regular.ttf), [Bold](output-fonts/LigaCousine-Bold.ttf)  
    * [DejaVu Sans Mono](output-fonts/LigaDejaVuSansMono.ttf)  
    * [Droid Sans Mono](output-fonts/LigaDroidSansMono.ttf)  
    * [edlo](output-fonts/Ligaedlo.ttf)  
    * [Hack](output-fonts/LigaHack-Regular.ttf)  
    * [Inconsolata](output-fonts/LigaInconsolata-Regular.ttf) & [Inconsolata-g](output-fonts/LigaInconsolata-g.ttf)  
    * IBM Plex Mono: [Regular](output-fonts/LigaIBMPlexMono-Regular.ttf), [Semibold](output-fonts/LigaIBMPlexMono-SemiBold.ttf)  
    * Meslo ([LGL](output-fonts/LigaMesloLGL-Regular.ttf), [LGLDZ](output-fonts/LigaMesloLGLDZ-Regular.ttf), [LGM](output-fonts/LigaMesloLGM-Regular.ttf), [LGMDZ](output-fonts/LigaMesloLGMDZ-Regular.ttf), [LGS](output-fonts/LigaMesloLGS-Regular.ttf), [LGSDZ](output-fonts/LigaMesloLGSDZ-Regular.ttf)  
    * [Oxygen Mono](output-fonts/LigaOxygenMono-Regular.ttf)  
    * [Roboto Mono](output-fonts/LigaRobotoMono-Regular.ttf)  
    * SF Mono: [Regular](output-fonts/LigaSFMono-Regular.ttf), [Semibold](output-fonts/LigaSFMono-Semibold.ttf)  
    * [Ubuntu Mono](output-fonts/LigaUbuntuMono-Regular.ttf)  

2.  A fontforge python script ([ligaturize.py](ligaturize.py)) that you can use to add the Fira Code ligatures to any other font you like.

Here's a couple examples of the fonts generated: SF Mono & Menlo with ligatures (note the `!=` and `->`):
![](images/sf-mono.png)
![](images/menlo.png)

## Requirements ##
**Using the Fonts**: See the [FiraCode README](https://github.com/tonsky/FiraCode) for a list of supported editors.

**Script**: This script requires FontForge python bindings. For Debian/Ubuntu they are available in `python-fontforge` package. For OpenSUSE and NixOS, they are included in the `fontforge` package. For macOS, they are available via brew (`brew install fontforge`).

## Using the Script ##
### Automatic ###

Use automatic mode to easily convert 1 or more font(s).

1. Put the font(s) you want into `input-fonts/`.
2.  Edit `ligatures.py` to disable any ligatures you don't want, and/or enable any (non-ligature) characters you want from Fira Code in addition to the ligatures.
3. Run `make`.
4. Retrieve the ligaturized fonts from `output-fonts/`.
5. The output fonts will be renamed with the prefix "Liga".

### Manual ###

1.  Move/copy the font you want to ligaturize into `input-fonts/` (or somewhere else convenient).
2.  Edit `ligatures.py` to disable any ligatures you don't want, and/or enable any (non-ligature) characters you want from Fira Code in addition to the ligatures.
3.  Run the script: `$ fontforge -lang=py ligaturize.py <INPUT> <OUTPUT>`, e.g. `$ fontforge -lang=py ligaturize.py input-fonts/Cousine-Regular.ttf output-fonts/CousineLigaturized-Regular.ttf`

The font family and weight for the output font (as recorded in the file) will be automatically set based on the name; if the output is `CousineLigaturized-Regular.ttf`, the font family will be `CousineLigaturized` and the font weight will be `Regular`. If no weight is specified, `Regular` is the default.

## Misc. ##
### Credit ###
This script was originally written by [IlyaSkriblovsky](https://github.com/IlyaSkriblovsky) for adding ligatures to DejaVuSans Mono ([dv-code-font](https://github.com/IlyaSkriblovsky/dv-code-font)). I made a few changes to generalize the script so that it works for any font, so that I could add ligatures to my favorite fonts. [ToxicFrog](https://github.com/ToxicFrog) has made a large number of contributions.

### Contributions ###
Contributions always welcome! Please submit a Pull Request, or create an Issue if you have an idea for a feature/enhancement (or bug).

### Related Projects ###
For more awesome programming fonts with ligatures, check out:  
1. [FiraCode](https://github.com/tonsky/FiraCode)  
2. [Hasklig](https://github.com/i-tu/Hasklig)  
