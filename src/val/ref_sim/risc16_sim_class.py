"""_summary_
"""

import os
from risc16_ops import Risc16Op, Risc16OpRRR, Risc16OpRRI, Risc16OpRI


class RFModel:
    _rf = [0] * 7

    def __init__(self, args) -> None:
        self.args = args

    def read(self, reg):
        if reg == 0:
            print(f"Reg{reg}: 0")
            return 0
        print(f"Reg{reg}: {self._rf[reg-1]}")
        return self._rf[reg-1]

    def write(self, reg, val):
        if reg != 0:
            self._rf[reg-1] = val
        print(f"Reg{reg} = {val}")

    def reset(self):
        self._rf = [0] * 7

    def __str__(self):
        """_summary_

        Returns:
            str: string representation of register file
        """
        retval = "---------Register File---------\n"
        for i, reg in enumerate(self._rf):
            retval += f"R{i+1}:{reg:04x}\n"
        return retval


class MEMModel:
    mem = {}

    def __init__(self, args, name="Memory") -> None:
        self.args = args
        self.name = name

    def read(self, addr):
        if addr not in self.mem:
            print(f"{self.name} read -- addr: {addr} - val: 0x0000")
            return 0
        print(f"{self.name} read -- addr: {addr} - val: {self.mem[addr]:#06x}")
        return self.mem[addr]

    def write(self, addr, data):
        if data != 0:
            self.mem[addr] = data & 0xffff
        elif addr in self.mem:
            del self.mem[addr]
        print(f"{self.name} write -- addr: {addr} - val: {data:#06x}")

    def load_program(self):
        """_summary_
        """
        self.mem = {}
        with open(self.args.program_file, 'r') as pf:
            addr = 0
            for line in pf:
                line_val = int(line.strip(), base=16)
                if line_val != 0:
                    self.mem[addr] = line_val
                addr += 1

    def __str__(self):
        """_summary_

        Returns:
            str: string representation of memory
        """
        retval = f"--------{self.name}--------\n"
        for addr, data in self.mem.items():
            retval += f"{addr:04x}:{data:04x}\n"
        return retval

    def reset(self):
        """_summary_
        """
        self.load_program()


class Risc16sim:
    """_summary_
    """
    instr_p = 0     # Model of instruction pointer or PC

    def __init__(self, args) -> None:
        self.args = args
        self.rf = RFModel(args)
        self.mem = MEMModel(args)

    def reset(self):
        self.rf.reset()
        self.mem.reset()
        self.instr_p = 0
        self._dump_state(f"{os.path.basename(self.args.program_file).split('.')[0]}_init_state.arch")

    def run(self, steps):
        for i in range(steps):
            print("-"*40)
            if self.instr_p > 0xffff:
                raise IndexError("There is an overflow in PC")
            instr = Risc16Op(self.mem.read(self.instr_p))
            print(f"Running step {i} -- pc: {self.instr_p} -> {instr}")
            print(f"Opcode: {instr.opcode.to_str} -- {instr.mnemonic.upper()}")
            if self._exec_instr(instr):  # if 1, it means halt
                break
        self._dump_state(f"{os.path.basename(self.args.program_file).split('.')[0]}_end_state.arch")

    def _exec_instr(self, instr):
        mnemonic = instr.mnemonic
        exec_func = f"_exec_{mnemonic}"
        if hasattr(self, exec_func):
            return getattr(self, exec_func)(instr)
        raise ValueError(f"Unsuported opcode {instr.opcode}")

    def _exec_add(self, instr):
        instr = Risc16OpRRR(instr)
        print(f"{instr}")
        wval = self.rf.read(instr.regB) + self.rf.read(instr.regC) & 0xffff
        self.rf.write(instr.regA, wval)
        self.instr_p += 1
        print(f"Next pc = {self.instr_p}")
        return 0

    def _exec_addi(self, instr):
        instr = Risc16OpRRI(instr)
        print(f"{instr}")
        wval = (self.rf.read(instr.regB) + instr.imm) & 0xffff
        self.rf.write(instr.regA, wval)
        self.instr_p += 1
        print(f"Next pc = {self.instr_p}")
        return 0

    def _exec_nand(self, instr):
        instr = Risc16OpRRR(instr)
        print(f"{instr}")
        wval = (~(self.rf.read(instr.regB) & self.rf.read(instr.regC))) & 0xffff
        self.rf.write(instr.regA, wval)
        self.instr_p += 1
        print(f"Next pc = {self.instr_p}")
        return 0

    def _exec_lui(self, instr):
        instr = Risc16OpRI(instr)
        print(f"{instr}")
        wval = instr.imm & 0xffc0
        self.rf.write(instr.regA, wval)
        self.instr_p += 1
        print(f"Next pc = {self.instr_p}")
        return 0

    def _exec_sw(self, instr):
        instr = Risc16OpRRI(instr)
        print(f"{instr}")
        addr = (self.rf.read(instr.regB) + instr.imm) & 0xffff
        self.mem.write(addr, self.rf.read(instr.regA))
        self.instr_p += 1
        print(f"Next pc = {self.instr_p}")
        return 0

    def _exec_lw(self, instr):
        instr = Risc16OpRRI(instr)
        print(f"{instr}")
        addr = (self.rf.read(instr.regB) + instr.imm) & 0xffff
        wval = self.mem.read(addr)
        self.rf.write(instr.regA, wval)
        self.instr_p += 1
        print(f"Next pc = {self.instr_p}")
        return 0

    def _exec_beq(self, instr):
        instr = Risc16OpRRI(instr)
        print(f"{instr}")
        if self.rf.read(instr.regA) == self.rf.read(instr.regB):
            self.instr_p += instr.imm
        self.instr_p += 1
        print(f"Next pc = {self.instr_p}")
        return 0

    def _exec_jalr(self, instr):
        instr = Risc16OpRRI(instr)
        print(f"{instr}")
        if instr.pseudo == "halt":
            return 1
        next_instr_p = self.rf.read(instr.regB)
        self.rf.write(instr.regA, self.instr_p + 1)
        self.instr_p = next_instr_p
        print(f"Next pc = {self.instr_p}")
        return 0

    def _dump_state(self, filename):
        with open(filename, 'w') as fp:
            fp.write(f"PC:{self.instr_p}\n")
            fp.write(str(self.rf))
            fp.write(str(self.mem))


def signed(uns_val, nbits=16):
    """Function that returns a signed integer from a nbits unsigned integer

    Args:
        uns_val (int): unsigned integer to be interpeted as as nbit signed integer
        nbits (int, optional): Number of bits to be used for interpreting the signed integer. Defaults to 16.

    Returns:
        int: The signed integer
    """
    max_val = 2**nbits
    return (uns_val - max_val) if uns_val > ((max_val/2)-1) else uns_val
