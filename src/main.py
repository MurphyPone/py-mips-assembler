#!/usr/bin/env python3

import sys
import os
from typing import List

from address import Address
from datum import Datum, write_symbol_table
from asm_parser import ParseResult, is_pseudo_command, translate_pseudo_command

def handle_args(argc, argv):
    write_symbols, input_file, output_file, symbol_file = False, None, None, None
    if argc == 3 and argv[1] == "-symbols":
        write_symbols = True 
        input_file = argv[2] 
        symbol_file = f"{input_file[:input_file.index('.')]}_symbols.txt"
        print(f"[MAIN] -- input file: {input_file}, symbol file: {symbol_file}")
        
        try:
            os.remove(symbol_file)
        except OSError:
            pass

    elif argc == 2:
        input_file = argv[1] # open(argv[1], "r")
        output_file = f"{input_file[:input_file.index('.asm')]}_output.o"
        
        try:
            os.remove(output_file)
        except OSError:
            pass

    return write_symbols, input_file, output_file, symbol_file

def main(argc: int, argv: List[str]):
    write_symbols, input_file, output_file, symbol_file = handle_args(argc, argv)
    
    symbols = []
    done_with_data = False
    address = Address()
    
    print(f"[MAIN] -- making first pass...")
    with open(input_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            
            # DEBUG
            if not line.startswith("#") and not line == "": 
                print(f"[MAIN] -- line: '{line}', address: {address}")

            if line.startswith("#") or line == "": 
                continue

            elif line == ".data":
                address.set_address(0x2000)
                print("[ADD] ", address)

            elif line == ".text":
                done_with_data = True 
                address.set_address(0x0000)

            elif not done_with_data: # we're reading data
                print("[ADD] -- pre: ", address)
                symbols.append(Datum(line, address))
                print("[ADD] -- post: ", address)

            elif ":" in line: # is a label
                name = line[:line.index(":")]
                instr_type = ".label"
                label = Datum(line, address, instr_type=instr_type, name=name)
                symbols.append(label)

            else: # is command
                address.increment(0x4)
                if "blt" in line:
                    address.increment(0x4)

    if write_symbols:
        write_symbol_table(symbol_file, symbols)
    
    print(f"[MAIN] -- making second pass...")
    with open (input_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            
            # DEBUG
            if not line.startswith("#") and not line == "": 
                print(f"[MAIN] -- line: '{line}', address: {address}")

            if line.startswith("#") or line == "":  
                pass

            elif line == ".data":
                pass # skip data on second pass

            elif line == ".text":
                address.set_address(0x0000)

            elif ":" in line: # is a label
                continue 

            else: # is a command
                if is_pseudo_command(line): # is a pseudo command
                    translate_pseudo_command(output_file, line, address, symbols)

                else: # is a normal command
                    command = ParseResult(line, address, symbols)
                    command.write_parse_result(output_file)

                address.increment(0x4)

    if not write_symbols:
        for i in range(len(symbols)-1):
            symbol = symbols[i]
            symbol.write_datum(output_file, symbols[i+1].instr_type)
        symbols[-1].write_datum(output_file, "last")

    return 0

if __name__ == "__main__":
    # import pdb
    # pdb.set_trace()
    main(len(sys.argv), sys.argv)
                

