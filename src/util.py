
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
    Register("$v3", 3),

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
    return "{0:016b}".format(Imm)

def translate_pseudo_command(line):
    pass

def is_pseudo_command(line):
    mnemonic = line.split()[0] 
    if mnemonic == "lw":
        if "(" in line: # not a special case
            return False 
        else:
            return True 
    
    return mnemonic in PSEUDO_COMMANDS


def binary_from_int(x: int):
    return "{0:05b}".format(x)

def get_26bit_rep(x: int):
    return "{0:026b}".format(1)