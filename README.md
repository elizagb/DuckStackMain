CREDIT: project guidelines and starter code from University of Oregon CIS 211 Spring Term 2022 
PROJECT GUIDELINES AND GIVEN CODE: https://github.com/UO-CIS211/duck-stack

Description adapted from https://github.com/UO-CIS211/duck-stack: 

The Duck Machine technology stack:  A CPU simulator, its assembler, and a compiler the language Mallard

This repository supports three projects in CIS 211 at University of Oregon. 

## Project 1:  A CPU simulator

A simulated CPU interprets Duck Machine instructions. Duck Machine machine
language instructions are encoded as 32 bit integers.  


- instruction_set : The (binary) instruction encoding for Duck 
  Machine processors.  The instruction set definitions were provided
  in `instr_format.py`; I wrote `bits.py` to support
  definition and manipulation of the bit fields in instruction words. 
- cpu : The CPU simulator. This simulator operates similarly to a 
  hardware CPU chip.  On each instruction cycle, it loads an 
  instruction from memory, decodes it (again using bitfields), and
  then executes it. 

## Project 2:  An assembler for Duck Machines

Two main tasks in translating assembly language to machine instructons: 

- Resolving adresses (e.g., determining the "target address" for a load, store, or jump instruction)
- Encoding instructions into the binary representation of the machine language

Most of the encoding was provided in "asm_encode".  I was responsible for creating "asm_resolve", 
which implements the first task. 

## Project 3:  Mallard compiler

Mallard is a high level language for Duck machines.
The source language for this compiler is Mallard, and the target language is Duck Machine 
assembly language. 

The front end is provided. I built the back end. 


