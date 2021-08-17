from typing import List
from address import Address

class Datum():
    bytes_written = 0 # static class variable
    def __init__(self, line, address: Address, instr_type=None, name=None):

        if instr_type == ".label":
            self.instr_type = instr_type
            self.name = name
            self.address = address.address

            return 

        self.name: str = None
        self.instr_type: str = None
        self.array: List[int] = None
        self.value: int = None
        self.txt: str = None # the actual string
        self.bin_str: str = None # the binary representation
        self.address: int = address.address # not a reference to the address flyweight, just the number

        split = line.split()
        self.name = split[0][:-1]
        self.instr_type = split[1]

        rest_of_str = " ".join(split[1:])

        if self.instr_type == ".word":
            if address.address % 4 != 0:
                padding_needed = 4 - (address.address % 4)
                address.set_address(padding_needed + address.address)
                self.address = address.address
        
            # check if data is a list
            if "," in rest_of_str or ":" in rest_of_str:
                self.array = []
                self.instr_type = ".word[]"

                rest_of_str = rest_of_str[len(".word"):]

                if "," in rest_of_str:
                    elems = rest_of_str.split(",")
                    for e in elems:
                        self.array.append(int(e))
                        address.increment(4)
                        
                else:
                    value, length  = rest_of_str.split(":")
                    value = int(value)
                    length = int(length)
                    self.array = [value] * length
                    address.increment(0x4 * length)
            
            # single value
            else: 
                self.value = int(split[2])
                address.increment(4)
        
        # it's a string 
        elif self.instr_type == ".asciiz":
            rest_of_str = ' '.join(rest_of_str.split()[1:])
            self.txt = rest_of_str[1:-1] # discard quoation marks
            self.txt += "\0"
            self.bin_str = ""
            for c in  self.txt:
                self.bin_str += "{0:08b}".format(ord(c))
                address.increment(1)     

    def __repr__(self):
        res = f"name: '{self.name}'\n"
        res += f"\ttype: {self.instr_type}\n"
        res += f"\taddress: {self.address}\n"

        if self.instr_type == ".word[]":
            res += f"array: {self.array}"
        elif self.instr_type == ".word":
            res += f"\tvalue: {self.value}"
        elif self.instr_type == ".asciiz":
            res += f"\ttext: {self.txt}"
            res += f"\tstr: {self.bin_str}"

        return res + "]]" 

    
    def write_datum(self, output_file, type_next):

        with open(output_file, "a") as f:
            # If starting the data section and the first datum is not a .word
            if Datum.bytes_written == 0 and self.instr_type != ".word":
                f.write("\n")

            if self.instr_type == ".word":
                binary = "{0:032b}".format(self.value if self.value >= 0 else (1<<32) + self.value)
                f.write(f"\n{binary}")
                Datum.bytes_written += 4
            
            elif self.instr_type == ".word[]":
                f.write("\n")
                for i, word in enumerate(self.array):
                    binary = "{0:032b}".format(word if word >= 0 else (1<<32) + word)
                    f.write(f"{binary}")
                    Datum.bytes_written += 4
                    
                    if i != len(self.array): # TODO might need to -1 here
                        f.write("\n")


            elif self.instr_type == ".asciiz":
                for char in self.txt:
                    # print(f"{self.txt} {char}", Datum.bytes_written)
                    if Datum.bytes_written % 4 == 0 and Datum.bytes_written != 0:
                        f.write("\n")
                    byte = "{0:08b}".format(ord(char))
                    f.write(byte)
                    Datum.bytes_written += 1

                if type_next != ".asciiz": # need to align
                    bits_of_padding_needed = 32 - len(self.bin_str) % 32
                    if bits_of_padding_needed != 32:
                        padding = "0" * bits_of_padding_needed
                        f.write(f"{padding}\n")
                    Datum.bytes_written += int(bits_of_padding_needed / 8)


def write_symbol_table(output_file, symbols):
    with open(output_file, "w") as f:
        for symbol in symbols:
            address = "{0:08b}".format(symbol.address)
            f.write(f"0x{address}:\t {symbol.name}\n")


        
