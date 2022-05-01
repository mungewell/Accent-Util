# Accent-Util
Utils for the M-Audio Accent Module

The Accent Module is somewhat limited in operation, it provides very
little access to configure it remotely and misses the ability to manage
patches.

The FW image contains a User section which holds 2 copies of the patches
(on for active, and other which is used during a factory reset).

The `decode_presets.py` contains a method for dumping the patches into 
a Python 'Construct' object, which can then be processed and written back
into the FW image.

On upload the unit does NOT checksum the FW image, which allows us to make
changes to it... but also exposes a large risk. Be careful!!!

```
$ python3 decode_presets.py -h               
usage: decode_effect [-h] [-d] [-t TARGET] [-o OUTFILE] FILE

positional arguments:
  FILE                  File to process

optional arguments:
  -h, --help            show this help message and exit
  -d, --dump            dump configuration to text
  -t TARGET, --target TARGET
                        location in FW image
  -o OUTFILE, --output OUTFILE
                        write data to OUTFILE
```

# Working with Presets

This script enables dumping the presets from the FW image with `--dump` or `-d`.

```
$ python3 decode_presets.py -d FW_update.FUP
Container: 
    patches = ListContainer: 
        Container: 
            number = 0
            name = u'Piano' (total 5)
            type = (enum) piano 1
            buttons = ListContainer: 
                Container: 
                    instrument = (enum) Piano 1
                    unknown1 = 0
                    unknown2 = 0
                    unknown3 = 0
                    colour = (enum) red 9
                    part = (enum) auto 3
                    low-note = 0
                    high-note = 87
                    channel = (enum) all 16
                    cc-num = 8
                    enabled = 1
                    unknown4 = (enum) max 3
                Container: 
...
```

The presets are parsed into a Python object, can be adjusted as need be. The object can be rebuilt back into the binary blob and written back into the FW image.

This is done in the tests I have been performing.
```
$ python3 decode_presets.py -o test.FUP FW_update.FUP
```
