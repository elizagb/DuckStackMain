"""
Duck Machine model DM2022 CPU

Eliza Black
CIS 211 Spring Term 2022
"""

import context  #  Python import search from project root
from instruction_set.instr_format import Instruction, OpCode, CondFlag, decode

from cpu.memory import Memory
from cpu.register import Register, ZeroRegister
from cpu.mvc import MVCEvent, MVCListenable

# For debugging we may want to log some events
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


# where calculations like addition, subtraction, multiplication, and division take place
class ALU(object):
    """The arithmetic logic unit (also called a "functional unit"
    in a modern CPU) executes a selected function but does not
    otherwise manage CPU state. A modern CPU core may have several
    ALUs to boost performance by performing multiple operatons
    in parallel, but the Duck Machine has just one ALU in one core.
    """
    # The ALU chooses one operation to apply based on a provided
    # operation code.  These are just simple functions of two arguments;
    # in hardware we would use a multiplexer circuit to connect the
    # inputs and output to the selected circuitry for each operation.
    ALU_OPS = {
        OpCode.ADD: lambda x, y: x + y,
        OpCode.SUB: lambda x, y: x - y,
        OpCode.MUL: lambda x, y: x * y,
        OpCode.DIV: lambda x, y: x // y,
        #
        # For memory access operations load, store, the ALU
        # performs the address calculation
        OpCode.LOAD: lambda x, y: x + y,
        OpCode.STORE: lambda x, y: x + y,
        # Some operations perform no operation
        OpCode.HALT: lambda x, y: 0
    }

    def exec(self, op: OpCode, in1: int, in2: int) -> tuple[int, CondFlag]:
        try:
            op_result = self.ALU_OPS[op](in1, in2)
        except:
            return (0, CondFlag.V)
        else:
            if op_result == 0:
                return (op_result, CondFlag.Z)
            elif op_result < 0:
                return (op_result, CondFlag.M)
            elif op_result > 0:
                return (op_result, CondFlag.P)


class CPUStep(MVCEvent):
    """CPU is beginning step with PC at a given address"""
    def __init__(self, subject: "CPU", pc_addr: int,
                 instr_word: int, instr: Instruction)-> None:
        self.subject = subject
        self.pc_addr = pc_addr
        self.instr_word = instr_word
        self.instr = instr


class CPU(MVCListenable):
    """Duck Machine central processing unit (CPU)
    has 16 registers (including r0 that always holds zero
    and r15 that holds the program counter), a few
    flag registers (condition codes, halted state),
    and some logic for sequencing execution.  The CPU
    does not contain the main memory but has a bus connecting
    it to a separate memory.
    """
    def __init__(self, memory: Memory):
        super().__init__()
        self.memory = memory  # Not part of CPU; what we really have is a connection

        self.registers = [ZeroRegister(), Register(), Register(), Register(),
                          Register(), Register(), Register(), Register(),
                          Register(), Register(), Register(), Register(),
                          Register(), Register(), Register(), Register()]
        self.condition = CondFlag.ALWAYS
        self.halted = False
        self.alu = ALU()
        self.pc = self.registers[15]

    # carries out one fetch/decode/execute cycle
    def step(self):
        """One fetch/decode/execute step"""
        # 1) Fetch an instruction

        # to fetch an instruction, first we get the address from
        # register 15, using the get method of the Register class
        instr_addr = self.pc.get()

        # use the address to read the instruction word from
        # memory, using the get method of the Memory class
        instr_word = self.memory.get(instr_addr)

        # 2) Decode
        instr = decode(instr_word)

        # Display the CPU state when we have decoded the instruction,
        # before we have executed it
        self.notify_all(CPUStep(self, instr_addr, instr_word, instr))

        # 3) Execute

        instr_predicate = self.condition & instr.cond  # check the instruction predicate
        if instr_predicate:
            left_op = self.registers[instr.reg_src1].get()
            right_op = self.registers[instr.reg_src2].get() + instr.offset
            result = self.alu.exec(instr.op, left_op, right_op)  # calculate a result value and new condition code

            # BEFORE we save the result value and instruction code,
            # we increment the program counter (register 15).
            self.pc.put(self.pc.get() + 1)

            # Then, after incrementing the program counter, we complete the operation.
            if instr.op is OpCode.STORE:
                addr = result[0]  # use the result of the calculation as a memory address

                # save the value of the register specified by instr.reg_target to that location in memory
                value = self.registers[instr.reg_target].get()
                self.memory.put(addr, value)

            elif instr.op is OpCode.LOAD:
                addr = result[0]
                # fetch the value of that location in memory:
                location_val = self.memory.get(addr)
                # storing it in the register specified by instr.reg_target
                self.registers[instr.reg_target].put(location_val)

            elif instr.op is OpCode.HALT:
                self.halted = True

            else:
                # For the other operations (ADD, SUB, MUL, DIV) we store the
                # result of the calculation in the register specified by instr.reg_target
                # and store the new condition code in the condition field of the CPU.
                self.registers[instr.reg_target].put(result[0])
                self.condition = result[1]
        else:
            self.pc.put(self.pc.get() + 1)

    def run(self, from_addr=0,  single_step=False) -> None:
        self.halted = False
        self.registers[15].put(from_addr)
        step_count = 0
        while not self.halted:
            if single_step:
                input(f"Step {step_count}; press enter")
            self.step()
            step_count += 1
