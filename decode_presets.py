# Util for dumping presets from Accent Module FW image

# Requires:
# https://github.com/construct/construct

from construct import *

'''
Patch:
1f
^^ Patch 32

50 72 65 73 65 74 20 33 32 00 00 00 00 00 00 
^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ^^ ASCII name

Buttons 1..8:
00 00 00 00 09 03 00 57 10 08 00 03 00 00 00 00 
                           ^^ CC
                        ^^ Chn#, 0x10 - All
                     ^^ HiNote?
                  ^^ LoNote
               ^^ Part? (Auto)
            ^^ Colour (Red)
^^ Instrument : 00 = undefined
00 00 00 00 09 03 00 57 10 0c 00 03 00 00 00 00 
00 00 00 00 09 03 00 57 10 0d 00 03 00 00 00 00 
00 00 00 00 09 03 00 57 10 0e 00 03 00 00 00 00 
00 00 00 00 09 03 00 57 10 0f 00 03 00 00 00 00 
00 00 00 00 09 03 00 57 10 10 00 03 00 00 00 00 
00 00 00 00 09 03 00 57 10 11 00 03 00 00 00 00 
00 00 00 00 09 03 00 57 10 12 00 03 00 00 00 00 

Faders 1..9(?):
13 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
         ^^ Max
      ^^ Min
   ^^ Chn (Auto)
^^ CC#
14 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
15 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
16 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
17 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
18 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
19 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
1a 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
1b 10 00 7f 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
'''

BUTTON = Struct(
    "instrument" / Byte,
    Const(b'\x00\x00\x00'),
    "colour" / Enum(Byte, 
        lt_green=0, green=1, turquosie=2,
        cyan=3, azure=4, blue=5, purple=6,
        pink=7, rose=8, red=9,
        orange=10, yellow=11, white=12,
    ),

    "part" / Enum(Byte, auto=3),
    "low-note" / Byte,
    "high-note" / Byte,
    "channel" / Enum(Byte, all=16),
    "cc-num" / Byte,
    "enabled" / Byte,

    Const(b'\x03'),
    Const(b'\x00\x00\x00\x00'),
)

FADER = Struct(
    "cc-num" / Byte,
    "channel" / Byte,
    "low-val" / Byte,
    "high-val" / Byte,

    Const(b'\x00'*12),
)

PATCH = Struct(
    "number" / Byte,
    "name" / PaddedString(14, "ascii"),
    "type" / Enum(Byte, multi=0, piano=1),
    "buttons" / Array(8, BUTTON),
    "faders" / Array(9, FADER),

    Const(b'\x00'*16),
)

PATCHES = Struct(
    "patches" / Array(32, PATCH),
)

#--------------------------------------------------

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="decode_effect")
    parser.add_argument('files', metavar='FILE', nargs=1,
        help='File to process')

    parser.add_argument("-d", "--dump",
        help="dump configuration to text",
        action="store_true", dest="dump")

    # FW 1.00.09
    # Active: 2105420 (0x0020204C)
    # Reset:  2117708 (0x0020504C)
    # Patches are 9728 bytes long

    parser.add_argument("-t", "--target", type=int,
        help="location in FW image", dest="target",
        default=2105420)

    parser.add_argument("-o", "--output", dest="outfile",
        help="write data to OUTFILE")

    options = parser.parse_args()

    if not len(options.files):
        parser.error("FILE not specified")

    # Read data from file
    infile = open(options.files[0], "rb")
    if not infile:
        sys.exit("Unable to open FILE for reading")
    else:
        data = infile.read()
    infile.close()

    if data:
        config = PATCHES.parse(data[options.target:
            options.target+9728])

        if options.dump:
            print(config)

        if options.outfile:
            # test, make all patches the same as patch 0
            for patch in range(1,32):
                print("cloning to patch %d" % patch)

                config['patches'][patch] = config['patches'][0].copy()
                config['patches'][patch]['number'] = patch

            new_patch = PATCHES.build(config)

            outfile = open(options.outfile, "wb")

            outfile.write(data[:options.target])
            outfile.write(new_patch)
            outfile.write(data[options.target+9728:])

            outfile.close

if __name__ == "__main__":
    main()
