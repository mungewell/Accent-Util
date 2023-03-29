# Attempt to communicate with the HydraSynth using the reverse-engineered SysEx protocol
# https://github.com/eclab/edisyn/blob/master/edisyn/synth/asmhydrasynth/sysex/SysexEncoding.txt

import crcmod
import binascii
import mido

class asm(object):
    inport = None
    outport = None

    id = b"\x00\x6F"                # ASM HydraSynth
    midiname = "HYDRASYNTH"         # when connected via USB


    def is_connected(self):
        if self.inport == None or self.outport == None:
            return(False)
        return(True)

    def connect(self, midiskip=0, id=None, midiname=None):
        inport = None
        outport = None
        
        if id:
            self.id = id
            print("Using ID:", binascii.hexlify(self.id))

        if midiname:
            self.midiname = midiname

        skip = midiskip
        for port in mido.get_input_names():
            if port[:len(self.midiname)]==self.midiname:
                if not skip:
                    self.inport = mido.open_input(port)
                    break
                else:
                    skip = skip - 1

        skip = midiskip
        for port in mido.get_output_names():
            if port[:len(self.midiname)]==self.midiname:
                if not skip:
                    self.outport = mido.open_output(port)
                    break
                else:
                    skip = skip - 1

        return self.is_connected()

    def disconnect(self):
        self.inport = None
        self.outport = None

    def checksum(self, data):
        crc32 = crcmod.Crc(0x104c11db7, rev=True, initCrc=0, xorOut=0xFFFFFFFF)
        crc32.update(data)

        return (crc32.crcValue ^ 0xFFFFFFFF).to_bytes(4, byteorder='little')

    def build_packet(self, data):
        return b"\x00\x20\x2B" + self.id + \
                binascii.b2a_base64(self.checksum(data) + data, newline=False)

    def validate(self, data):
        if data[:4] == self.checksum(data[4:]):
            return True
        return False

    def send(self, data):
        msg = mido.Message("sysex", data = self.build_packet(data))
        #print(binascii.hexlify(bytes(msg.data)))
        self.outport.send(msg)
        
    def recv(self):
        # This is blocking...
        msg = self.inport.receive()

        while msg.type == "clock":
            msg = self.inport.receive()

        decode = binascii.a2b_base64(bytes(msg.data[5:]))

        if self.validate(decode):
            return decode[4:]
        return None

    def send_n_recv(self, data):
        self.send(data)
        return self.recv()

    def header(self):
        return self.send_n_recv(b"\x18\x00")

    def footer(self):
        return self.send_n_recv(b"\x1A\x00")

    def names(self, bank):
        names = b""
        self.header()

        #msg = mido.Message("sysex", data = self.build_packet(b"\x02\x00"+bytes(chr(bank), "ascii")))
        msg = mido.Message("sysex", data = self.build_packet(bytes([0x02, 0x00, bank])))
        self.outport.send(msg)

        for chunk in range(19):
            resp = self.recv()
            names += resp[4:]
            #print(binascii.hexlify(resp))

            if not resp:
                break

            #msg = mido.Message("sysex", data = self.build_packet(b"\x17\x00"+bytes(chr(chunk), "ascii")+b"\x13"))
            msg = mido.Message("sysex", data = self.build_packet(bytes([0x17, 0x00, chunk, 0x13])))
        
            #decode = binascii.a2b_base64(bytes(msg.data[5:]))
            #print(binascii.hexlify(decode))

            self.outport.send(msg)

        self.footer()

        return names

#--------------------------------------------------
def main():
    from argparse import ArgumentParser
    from hexdump import hexdump

    parser = ArgumentParser(prog="asm")

    parser.add_argument("-M", "--midiskip",
        type=int, default=0, dest="midiskip",
        help="Skip devices when connecting, ie when you have multiple Keyboards")
    parser.add_argument("-N", "--midiname",
        default=None, dest="midiname",
        help="Specify Midi Device name")

    parser.add_argument("-n", "--names", type=int,
        help="Download patch names ('1' for bank A, etc)", dest="names")

    parser.add_argument("--akx10", action="store_true", 
        help="Attempt coms with AKX10", dest="akx10")
    parser.add_argument("--accentm", action="store_true", 
        help="Attempt coms with Accent Module", dest="accent")

    options = parser.parse_args()

    keyboard = asm()
    if options.akx10:
        keyboard.connect(options.midiskip, midiname=options.midiname, \
                id = b"\x00\x03")
    elif options.accent:
        keyboard.connect(options.midiskip, midiname=options.midiname, \
                id = b"\x61\x0B")
    else:
        keyboard.connect(options.midiskip, midiname=options.midiname)

    if keyboard.is_connected():
        # Handshake
        print(hexdump(keyboard.send_n_recv(b"\x00\x00")))

        # Read version
        print(hexdump(keyboard.send_n_recv(b"\x28\x00")))

        if options.names:
            print("Download bank %d" % options.names)
            print(hexdump(keyboard.names(options.names)))

if __name__ == "__main__":
    main()

