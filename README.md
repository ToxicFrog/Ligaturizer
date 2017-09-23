# Ligaturizer #

![](img.png)

**Add ligatures to any coding font!**

What this repo contains:
1.  Programming fonts with ligatures added (in `output-fonts/`), including:
  * Anonymous Pro
  * CamingoCode
  * Cousine
  * DejaVu Sans Mono
  * Droid Sans Mono
  * Hack
  * Inconsolata-g
  * Inconsolata
  * Meslo (sizes: LGL, LGLDZ, LGM, LGMDZ, LGS, LGSDZ)
  * Oxygen Mono
  * Roboto Mono
  * SF Mono
  * Ubuntu Mono
  * edlo
2.  A script [ligaturize.py](ligaturize.py) that adds the ligatures from [Fira Code](https://github.com/tonsky/FiraCode) to a font without ligatures

**Credit**: This awesome script was written by [IlyaSkriblovsky](https://github.com/IlyaSkriblovsky) for adding ligatures to Deja Vu Sans Mono ([dv-code-font](https://github.com/IlyaSkriblovsky/dv-code-font)). I've just made a few minor changes to generalize the script so that it works for any given font.

## Requirements ##
**Script**: This script requires FontForge python bindings. For Debian/Ubuntu they are available in `python-fontforge` package. For macOS,
they are available via brew (`brew install fontforge`).

**Using the Fonts**: See the [FiraCode README](https://github.com/tonsky/FiraCode) for a list of supported editors.

## Using the Script ##
1.  Move/copy the font you want to ligaturize into `input-fonts/`
2.  Run the script: `$ fontforge -lang=py ligaturize.py`
3.  You'll be prompted for the name of the font, and the name for the generated font. Example:

```shell
❯ fontforge -lang=py ligaturize.py
    ...
Enter the source font filename (including extension): RobotoMono-Regular.ttf
Enter a name for your ligaturized font -- or press ENTER to use the same name: <PRESS ENTER>
    ...
Generated ligaturized font Roboto Mono L in ligaturized-fonts/RobotoMono.ttf
```

```shell
❯ fontforge -lang=py ligaturize.py
    ...
Enter the source font filename (including extension): RobotoMono-Regular.ttf
Enter a name for your ligaturized font -- or press ENTER to use the same name: RobotoMonoL
    ...
Generated ligaturized font Roboto Mono L in ligaturized-fonts/RobotoMonoL.ttf
```

If you don't provide a name for the new font, it will have the same name as the input font.

## Misc. ##

For more awesome programming fonts with ligatures, check out:
1. [FiraCode](https://github.com/tonsky/FiraCode)
2. [Hasklig](https://github.com/i-tu/Hasklig)
