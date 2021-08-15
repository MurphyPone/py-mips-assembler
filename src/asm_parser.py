# from util import classify, binary_from_int, get_26bit_rep, reg_lookup, get_opcode, get_function, get_IMM
import ctypes
from typing import List
from datum import Datum

# util 

R_INSTRUCTIONS = ["mul", "sub", "add", "nor", "addu", "slt", "srav"]
I_INSTRUCTIONS = ["addi", "lui", "lw", "sw", "slti", "addiu", "beq", "bne", "sra", "sll", "blez", "bgtz"]
S_INSTRUCTIONS = ["mult", "syscall", "j"]

PSEUDO_COMMANDS = ["move", "blt", "la", "li", "nop"]

class Register():
    def __init__(self, name, num):
        self.name = name 
        self.num = num

class Instruction():
    def __init__(self, name, instr_type, opcode, function_code):
        self.name = name 
        self.instr_type = instr_type
        self.opcode = opcode
        self.function_code = function_code

REGISTERS = [
    Register("$zero", 0),
    Register("$at", 1),
    Register("$v0", 2),
    Register("$v1", 3),

    Register("$a0", 4),
    Register("$a1", 5),
    Register("$a2", 6),
    Register("$a3", 7),

    Register("$t0", 8),
    Register("$t1", 9),
    Register("$t2", 10),
    Register("$t3", 11),
    Register("$t4", 12),
    Register("$t5", 13),
    Register("$t6", 14),
    Register("$t7", 15),
    
    Register("$s0", 16),
    Register("$s1", 17),
    Register("$s2", 18),
    Register("$s3", 19),
    Register("$s4", 20),
    Register("$s5", 21),
    Register("$s6", 22),
    Register("$s7", 23),

    Register("$t8", 24),
    Register("$t9", 25),
    
    Register("$k0", 26),
    Register("$t1", 27),
]

INSTRUCITONS = [
    Instruction("mul", "R", "011100", "000010"),
    Instruction("mul",  "R", "011100", "000010"),
    Instruction("add",  "R", "000000", "100000"),
    Instruction("sub",  "R", "000000", "100010"),
    Instruction("addi", "I", "001000", None),
    Instruction("lui",  "I", "001111", None),
    Instruction("lw",   "I", "100011", None),
    Instruction("mult", "S", "000000", "011000"),

    Instruction("nor",  "R", "000000", "100111"),
    Instruction("slti", "I", "001010", None),
    Instruction("syscall","S","000000", "001100"),

    Instruction("sw",   "I", "101011", None),
    Instruction("addu", "R", "000000", "100001"),
    Instruction("sll",  "I", "000000", "000000"),
    Instruction("slt",  "R", "000000", "101010"),
    Instruction("sra",  "I", "000000", "000011"),
    Instruction("srav", "R", "000000", "000111"),
    Instruction("addiu","I", "001001", None ),
    Instruction("beq",  "I", "000100", None ),
    Instruction("bne",  "I", "000101", None ),
    Instruction("blez", "S", "000110", None ),
    Instruction("bgtz", "S", "000111", None ),
    Instruction("j",    "S", "000010", None),
]

def classify(mnemonic: str):
    if mnemonic in R_INSTRUCTIONS:
        return "R"
    elif mnemonic in I_INSTRUCTIONS:
        return "I"
    elif mnemonic in S_INSTRUCTIONS:
        return "S"
    else:
        print("error in classify")
        raise(Exception)


def reg_lookup(reg_name: str):
    for register in REGISTERS:
        if register.name == reg_name:
            return register.num

    return 255

def get_opcode(mnemonic: str):
    for instruction in INSTRUCITONS:
        if mnemonic == instruction.name:
            return instruction.opcode
    
    return None

def get_function(mnemonic: str):
    for instruction in INSTRUCITONS:
        if mnemonic == instruction.name:
                return instruction.function_code

def get_IMM(Imm):
    return "{0:016b}".format(Imm if Imm >= 0 else (1<<16) + Imm)

def translate_pseudo_command(output_file, line, address, labels: List[Datum]):
    split = line.split()
    mnemonic = split[0]
    rest_of_str = " ".join(split[1:])

    if mnemonic == "move": # ret addu, rd, zero, rs
        rd, rs = split[1], split[2]
        subcommand = f"addu\t{rd}, $zero, {rs}"
        
        command = ParseResult(subcommand, address, labels)
        command.write_parse_result(output_file)
    
    elif mnemonic == "blt":
        rs    = split[1]
        rt    = split[2]
        label = split[3]

        subcommand_slt = f"slt\t$at, {rs}, {rt}"
        subcommand_bne = f"bne\t$at, $zero {label}"
        
        command = ParseResult(subcommand_slt, address, labels)
        command.write_parse_result(output_file)

        address += 4 # TODO this is gonna cause a problem...

        command = ParseResult(subcommand_bne, address, labels)
        command.write_parse_result(output_file)

    elif mnemonic == "la":
        rt, label = split[1], split[2]

        for lbl in labels:
            if lbl.name == label:
                subcommand = f"addi\t{rt}, $zero, {lbl.address}"
                command = ParseResult(subcommand, address, labels)
                command.write_parse_result(output_file)

    elif mnemonic == "li":
        rt, offset = split[1], split[2]
        subcommand = f"addiu\t{rt}, $zero, {offset}"
        command = ParseResult(subcommand, address, labels)
        command.write_parse_result(output_file)

    elif mnemonic == "lw":
        rt, label = split[1], split[2]

        for lbl in labels:
            if lbl.name == label:
                subcommand = f"lw\t{rt}, {lbl.address}($zero)"
                command = ParseResult(subcommand, address, labels)
                command.write_parse_result(output_file)
    
    elif mnemonic == "nop":
        subcommand = f"sll\t$zero, $zero, 0"
        command = ParseResult(subcommand, address, labels)
        command.write_parse_result(output_file)

def is_pseudo_command(line):
    mnemonic = line.split()[0] 
    if mnemonic == "lw":
        if "(" in line: # not a special case
            return False 
        else:
            return True 
    
    return mnemonic in PSEUDO_COMMANDS

def binary_from_int(x: int):
    return "{0:05b}".format(x if x >= 0 else (1<<5) + x)

def get_26bit_rep(x: int):
    return "{0:026b}".format(x if x >= 0 else (1<<26) + x)

## 


class ParseResult():
    def __init__(self, asm, current_address, symbols):
        """Breaks up the given MIPS32 assembly instruction and creates a proper
       ParseResult object storing information about that instruction

       PRE: asm is an array holding the representation of a syntactically
            valid assembly instruction, whose mnemonic is one of the following

                add, addi, and, andi, lui, lw, sub 
            
            formatted  as follows:

                <mnemonic><ws><operand1>,<ws><operand2>,<ws>...

            where <ws> is an arbitrary mixture of tab and space characters

        Returns:
            a properly formed ParseResult object whose fields have been correctly
            initialized to correspond to the target of p_asm

        """
        self.ASM_instruction = asm
        self.mnemonic: str = None
        self.rd_name: str = None
        self.rs_name: str = None
        self.rt_name: str = None
        rd, rs, rt = 255, 0, 255, 
        self.Imm: ctypes.c_int16 = None
        self.opcode: str = None
        self.function: str = None
        self.rd: str = None
        self.rs: str = None
        self.rt: str = None
        self.IMM: str = None
        self.jump_address: str = None
        self.instr_type: str = None

        split = asm.replace(",", "").split()
        self.mnemonic = split[0]
        
        self.instr_type = classify(self.mnemonic) 

        if self.instr_type == "R":
            if self.mnemonic == "srav":
                self.rd_name = split[1]
                self.rt_name = split[2]
                self.rs_name = split[3]
            else:
                self.rd_name = split[1]
                self.rs_name = split[2]
                self.rt_name = split[3]

        elif self.instr_type == "I":
            if self.mnemonic == "addi" or self.mnemonic == "slti":
                self.rt_name = split[1]
                self.rs_name = split[2]
                self.Imm     = int(split[3])
            
            elif self.mnemonic == "addiu":
                self.rt_name = split[1]
                self.rs_name = split[2]
                self.Imm     = int(split[3])

            elif self.mnemonic == "sra" or self.mnemonic == "sll":
                self.rd_name = split[1]
                self.rt_name = split[2]
                shift_amt    = split[3]
                self.rs      = binary_from_int(shift_amt)

            elif self.mnemonic == "lui":
                self.rt_name = split[1]
                self.Imm     = int(split[3])
                self.rs      = "00000"

            elif self.mnemonic == "bglez" or self.mnemonic == "bgtz":
                self.rs_name = split[1]
                label        = split[2]
                self.Imm     = int(split[3])

                for symbol in symbols:
                    if symbol.name == label:
                        self.Imm = int((symbol.address - current_address -4) / 4 )

            elif self.mnemonic == "bne" or self.mnemonic == "beq":
                self.rs_name = split[1]
                self.rt_name = split[2]
                label        = split[3] 

                for symbol in symbols:
                    if symbol.name == label:
                        self.Imm = int((symbol.address - current_address -4) / 4 )

            elif self.mnemonic == "lw" or self.mnemonic == "sw":
                self.rt_name = split[1]
                
                mess = split[2].replace("(", " ").replace(")", " ").split()
                self.rs_name = mess[1]
                self.Imm     = int(mess[0])

                print(self.rt_name, self.rs_name, self.Imm)
        
        elif self.instr_type == "S":
            if self.mnemonic == "syscall":
                pass

            elif self.mnemonic == "j":
                label = split[1]
                
                for symbol in symbols:
                    if symbol.name == label:
                        self.jump_address = get_26bit_rep(symbol.address/4)

        else:
            print(f"Failed to classify mnemonic: {self.mnemonic}")

        if self.rd_name:
            rd = reg_lookup(self.rd_name)
            if rd != 255:
                self.rd = binary_from_int(rd)
        
        if self.rs_name:
            rs = reg_lookup(self.rs_name)
            if rs != 255:
                self.rs = binary_from_int(rs)

        if self.rt_name:
            rt = reg_lookup(self.rt_name)
            if rt != 255:
                self.rt = binary_from_int(rt)


        self.opcode = get_opcode(self.mnemonic)
        self.function = get_function(self.mnemonic)
        
        
        if self.Imm:
            self.IMM = get_IMM(self.Imm)
        else:
            self.Imm = 0
            self.IMM = get_IMM(self.Imm)

    def __repr__(self):
        res = f"{self.ASM_instruction}\n"
        res += f"\t{self.opcode}\t{self.mnemonic}\n"
        res += f"\t{self.rd}\t{self.rd_name}\n"
        res += f"\t{self.rs}\t{self.rs_name}\n"
        res += f"\t{self.rt}\t{self.rt_name}\n"
        res += f"\t{self.function}\n"
        res += f"\t{self.Imm}\t{self.IMM}\n"

        return res


    def write_parse_result(self, output_file):
        """writes the contents of the ParseResult to an output file"""

        with open(output_file, "a") as f:
            if self.instr_type == "R":
                f.write(f"{self.opcode}{self.rs}{self.rt}{self.rd}00000{self.function}\n")
            
            elif self.instr_type == "I":
                if self.mnemonic == "slti":
                    f.write(f"{self.opcode}{self.rs}{self.rt}{self.IMM}\n")
                
                elif self.mnemonic == "sra" or self.mnemonic == "sll":
                    f.write(f"{self.opcode}00000{self.rt}{self.rd}{self.rs}{self.function}\n")
                
                elif self.mnemonic == "blez" or self.mnemonic == "bgtz":
                    f.write(f"{self.opcode}{self.rs}00000{self.rd}{self.IMM}\n")
                
                else:
                    f.write(f"{self.opcode}{self.rs}{self.rt}{self.IMM}\n")

            elif self.instr_type == "S":
                if self.mnemonic == "syscall":
                    syscall_code = "00000000000000000000"
                    f.write(f"{self.opcode}{syscall_code}{self.function}\n")
                
                elif self.mnemonic == "mult":
                    mult_code = "0000000000"
                    f.write(f"{self.opcode}{self.rs}{self.rt}{mult_code}{self.function}\n")

                elif self.mnemonic == "j":
                    mult_code = "0000000000"
                    f.write(f"{self.opcode}{self.jump_address}\n")

    def write_parse_results(self, output_file, results):
        """writes a list of ParseResults to output file"""
        for result in results:
            result.write_parse_result(output_file)



    
