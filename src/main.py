#!/usr/bin/env python3

import sys
from typing import List

from datum import Datum, write_symbol_table
from util import is_pseudo_command, translate_pseudo_command
from asm_parser import ParseResult


def main(argc: int, argv: List[str]):
    write_symbols = False
    if argc == 4 and argv[1] == "-symbols":
        write_symbols = True 
        input_file = argv[2] # open(argv[2], "r")
        symbol_file = argv[3] # open(argv[3], "w")
    elif argc == 3:
        input_file = argv[1] # open(argv[1], "r")
        output_file = argv[2] # open(argv[2], "r")
    else:
        print("Too few arguments, try\t`assemble input.asm output.o")

    print(f"[MAIN] -- input file: {input_file}, output file: {output_file}")

    
    symbols = []
    done_with_data = False
    address = 0x0
    
    print(f"[MAIN] -- making first pass...")
    with open (input_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            print(f"[MAIN] -- line: '{line}'")

            if line.startswith("#") or line == "": 
                continue
            elif line == ".data":
                address = 0x2000 

            elif line == ".text":
                done_with_data = True 
                address = 0x0000 

            elif not done_with_data: # we're reading data
                symbols.append(Datum(line, address))

            elif ":" in line: # is a label
                name = line[:line.index(":")]
                instr_type = ".label"
                label = Datum(line, address, instr_type=instr_type, name=name)
                symbols.append(label)

            else: # is command
                address += 0x4
                if "blt" in line:
                    address += 0x4

    if write_symbols:
            write_symbol_table(symbol_file, symbols)
    
    print(f"[MAIN] -- making second pass...")
    with open (input_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            print(f"[MAIN] -- line: '{line}'")

            if line.startswith("#") or line == "":  
                continue

            elif line == ".data":
                continue # skip data on second pass

            elif line == ".text":
                done_with_data = True 
                address = 0x0000 

            elif not done_with_data: # we're reading data
                symbols.append(Datum(line, address))

            elif ":" in line: # is a label
                continue 

            else: # is a command
                if is_pseudo_command(line): # is a pseudo command
                    translate_pseudo_command(line)

                else: # is a normal command
                    command = ParseResult(line, address, symbols)
                    command.write_parse_result(output_file)

                address += 0x4 

    if write_symbols:
        for i in range(len(symbols)):
            symbol = symbols[i]
            symbol.write_datum(symbol_file, symbols[i].type)
        symbols[-1].write_datum(symbol_file, "last")

    return 0

if __name__ == "__main__":
    # import pdb
    # pdb.set_trace()
    main(len(sys.argv), sys.argv)
                

