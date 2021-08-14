from util import classify, binary_from_int, get_26bit_rep, reg_lookup, get_opcode, get_function, get_IMM
import ctypes


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
                self.Imm     = ctypes.c_int16(split[3])
            
            elif self.mnemonic == "addiu":
                self.rt_name = split[1]
                self.rs_name = split[2]
                self.Imm     = ctypes.c_uint16(split[3])

            elif self.mnemonic == "sra" or self.mnemonic == "sll":
                self.rd_name = split[1]
                self.rt_name = split[2]
                shift_amt    = split[3]
                self.RS      = binary_from_int(shift_amt)

            elif self.mnemonic == "lui":
                self.rt_name = split[1]
                self.Imm     = ctypes.c_int16(split[2])
                self.RS      = "00000"

            elif self.mnemonic == "bglez" or self.mnemonic == "bgtz":
                self.rs_name = split[1]
                label        = split[2]
                self.Imm     = ctypes.c_int16(split[3])

                for symbol in symbols:
                    if symbol.name == label:
                        self.Imm = ctypes.c_int16((symbol.address - current_address -4) / 4 )

            elif self.mnemonic == "bne" or self.mnemonic == "beq":
                self.rs_name = split[1]
                self.rt_name = split[2]
                label        = split[3] 

                for symbol in symbols:
                    if symbol.name == label:
                        self.Imm = ctypes.c_int16((symbol.address - current_address -4) / 4 )

            elif self.mnemonic == "lw" or self.mnemonic == "sw":
                self.rs_name = split[1]
                self.rt_name = split[2]
                self.Imm     = split[3]
        
        elif self.instr_type == "S":
            if self.mnemonic == "syscall":
                self.rs_name = split[1]
                self.rt_name = split[1]
                rd = 0

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

        with open(output_file, "w") as f:
            if self.instr_type == "r":
                f.write(f"{self.opcode}{self.RS}{self.RT}{self.RD}00000{self.function}\n")
            
            elif self.instr_type == "i":
                if self.mnemonic == "slti":
                    f.write(f"{self.opcode}{self.RS}{self.RT}{self.IMM}")
                
                elif self.mnemonic == "sra" or self.mnemonic == "sll":
                    f.write(f"{self.opcode}00000{self.RT}{self.RD}{self.RS}{self.function}\n")
                
                elif self.mnemonic == "blez" or self.mnemonic == "bgtz":
                    f.write(f"{self.opcode}{self.RS}00000{self.RD}{self.IMM}\n")
                
                else:
                    f.write(f"{self.opcode}{self.RS}{self.RT}{self.IMM}\n")

            elif self.instr_type == "s":
                if self.mnemonic == "syscall":
                    syscall_code = 00000000000000000000
                    f.write(f"{self.opcode}{syscall_code}{self.function}\n")
                
                elif self.mnemonic == "mult":
                    mult_code = 0000000000
                    f.write(f"{self.opcode}{self.RS}{self.RT}{mult_code}{self.function}\n")

                elif self.mnemonic == "j":
                    mult_code = 0000000000
                    f.write(f"{self.opcode}{self.jump_address}\n")

    def write_parse_results(self, output_file, results):
        """writes a list of ParseResults to output file"""
        for result in results:
            result.write_parse_result(output_file)



    
