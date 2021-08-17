# py-mips-assembler

A MIPS assembler written in Python.  This idea is an adaptation/extension of an assignment for a Computer Organization class and is therefore 

[![forthebadge](https://forthebadge.com/images/badges/built-with-resentment.svg)](https://forthebadge.com)

Supported instructions include:

| mnemonic | |
|----------|-|
| mul     |
| add     |
| sub     |
| addi    |
| lui     |
| lw      |
| mult    |
| nor     |
| slti    |
| syscall |
| sw      |
| addu    |
| sll     |
| slt     |
| sra     |
| srav    |
| addiu   |
| beq     |
| bne     |
| blez    |
| bgtz    |
| j       |

The definitions/taxonomy of each of these commands can be found in the [MIPS32™ Architecture For Programmers Volume II: The MIPS32™ Instruction Set](https://www.cs.cornell.edu/courses/cs3410/2008fa/MIPS_Vol2.pdf) (a real page turner).

## Use

`./main.py <input.asm>` will generate the relevant machine code for a valid assembly file with the name `input_output.o`.

## Testing 

`./tester.py <folder/test_ouput.o>` to test a single file against it's solution 

or 

`./tester.py -f <folder/>` to test every `_ouput.o` file within a directory.

## Contributing 

This was hacked together in a weekend - pls don't xoxo. I know it's gross 
