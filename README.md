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
