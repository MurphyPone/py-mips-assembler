from typing import List

class Datum():
    bytes_written = 0 # static class variable
    def __init__(self, line, address, instr_type=None, name=None):
        print(f"[DATUM] -- line in Datum constructor: '{line}'")
        
        if instr_type == ".label":
            self.instr_type = instr_type
            self.name = name

            return 
            
        self.last_was_asciiz = False

        self.name: str = None
        self.instr_type:str = None
        self.array: List[int] = None 
        self.txt: str = None # the actual string
        self.str: str = None # the binary representation
        self.address: int = address 

        split = line.split()
        self.name = split[0]
        self.instr_type = split[1]

        rest_of_str = " ".join(split[1:])

        if self.instr_type == ".word":
            if address % 4 != 0:
                padding_needed = 4 - (address % 4)
                self.address = padding_needed + address
        
            
            # check if data is a list
            if "," in rest_of_str or ":" in rest_of_str:
                self.array = []
                self.type = ".word[]"

                if "," in rest_of_str:
                    elems = rest_of_str.split(",")
                    for e in elems:
                        self.array.append(int(e))
                        self.address += 4

                
                else:
                    value, length  = rest_of_str.split(":")
                    value = int(value)
                    length = int(length)
                    self.array = [value] * length
                    
                    for i in range(self.length):
                        self.address += 0x4
            
            # single value
            else: 
                self.value = int(split[2])

            if self.last_was_asciiz:
                pass 

            self.last_was_asciiz = False 
        
        # it's a string 
        elif self.instr_type == ".asciiz":
            self.txt = split[2][1:-1] # discard quoation marks
            self.str = ""
            for c in  self.txt:
                self.str += "{0:08b}".format(ord(c))

            self.last_was_asciiz = True         


    def __repr__(self):
        res = f"name: {self.name}\n"
        res += f"\ttype: {self.instr_type}\n"
        res += f"\taddress: {self.address}\n"

        if self.instr_type == ".word[]":
            res += f"\tarray: {self.array}"
        elif self.instr_type == ".word":
            res += f"\value: {self.value}"
        elif self.instr_type == ".asciiz":
            res += f"\vtext: {self.txt}"
            res += f"\vstr: {self.str}"

        return res 

    
    def write_datum(self, output_file, type_next):
        print(f"[DATUM] -- output_file: {output_file}")
        bytes_written = 0

        with open(output_file, "w") as f:
            # If starting the data section and the first datum is not a .word
            if bytes_written == 0 and self.type == ".word":
                f.write("\n")

            if self.instr_type == ".word":
                binary = "{0:032b}".format(self.value)
                f.write(f"\n{binary}")
                bytes_written += 4
            
            elif self.instr_type == ".word[]":
                f.write(f"\n")
                for i in range(len(self.array)):
                    word = self.array[i]
                    binary = "{0:032b}".format(word)
                    f.write(f"{binary}")
                    bytes_written += 4
                    if i == len(self.array):
                        f.write("\n")

            elif self.instr_type == ".asciiz":
                for c in range(len(self.str+1)/8):
                    if bytes_written %4 == 0 and bytes_written != 0:
                        f.write("\n")
                    f.write(c)
                    bytes_written += 1

                if type_next == ".asciiz": # need to align
                    padding_needed = 32 - len(self.str) % 32
                    if padding_needed != 32:
                        f.write(f"{'0'*padding_needed}")
                    bytes_written += padding_needed / 8
                    

def write_symbol_table(output_file, symbols):
    with open(output_file, "w") as f:
        for symbol in symbols:
            address = "{0:08b}".format(symbol.address)
            f.write(f"0x{address}:\t {symbol.name}\n")


        
