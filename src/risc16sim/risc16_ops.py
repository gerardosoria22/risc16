from enum import IntEnum
# ---------------------------------------------------------------------------- #
#                              Instruction formats                             #
# ---------------------------------------------------------------------------- #


class Risc16Op:
    def __init__(self, instr=None) -> None:
        if isinstance(instr, int):
            self._raw_val = instr
        elif isinstance(instr, Risc16Op):
            self._raw_val = instr.get_raw_val()
        else:
            raise TypeError("instr must be either int or Risc16Op")

    @property
    def opcode(self):
        return Risc16Opcodes((self._raw_val >> 13) & 0b111)

    @property
    def mnemonic(self):
        return self.opcode.mnemonic

    @property
    def pseudo(self):
        return self.mnemonic

    def get_raw_val(self):
        return self._raw_val

    def __str__(self) -> str:
        return f"{self._raw_val:#06x}"


class Risc16OpRRR(Risc16Op):

    @property
    def regA(self):
        return (self._raw_val >> 10) & 0b111

    @property
    def regB(self):
        return (self._raw_val >> 7) & 0b111

    @property
    def regC(self):
        return (self._raw_val >> 0) & 0b111

    @property
    def pseudo(self):
        if self.opcode == Risc16Opcodes.OP_ADD and self.regA == 0 and self.regB == 0 and self.regC == 0:
            return "nop"
        return super().pseudo

    def __str__(self) -> str:
        return f"{self.pseudo.upper()} -- regA: {self.regA} - regB: {self.regB} - regC: {self.regC}"


class Risc16OpRRI(Risc16Op):

    @property
    def regA(self):
        return (self._raw_val >> 10) & 0b111

    @property
    def regB(self):
        return (self._raw_val >> 7) & 0b111

    @property
    def imm(self):
        """signed immediate (-64 to 63)

        Returns:
            int: signed immediate (-64 to 63)
        """
        unsigned_imm = (self._raw_val >> 0) & 0x7f
        return (unsigned_imm - 128) if unsigned_imm > 63 else unsigned_imm

    @property
    def pseudo(self):
        if self.opcode == Risc16Opcodes.OP_JALR and self.regA == 0 and self.regB == 0:
            return "halt"
        elif self.opcode == Risc16Opcodes.OP_ADDI and self.regA == self.regB and (self.imm > 0):
            return "lli"
        return super().pseudo

    def __str__(self) -> str:
        return f"{self.pseudo.upper()} -- regA: {self.regA} - regB: {self.regB} - imm: {self.imm}"


class Risc16OpRI(Risc16Op):

    @property
    def regA(self):
        return (self._raw_val >> 10) & 0b111

    @property
    def imm(self):
        return (self._raw_val >> 0) & 0x3ff

    def __str__(self) -> str:
        return f"{self.pseudo.upper()} -- regA: {self.regA} - imm: {self.imm}"


class Risc16Opcodes(IntEnum):
    OP_ADD = 0b000  # noqa: E221
    OP_ADDI = 0b001
    OP_NAND = 0b010
    OP_LUI = 0b011
    OP_SW = 0b100
    OP_LW = 0b101
    OP_BEQ = 0b110
    OP_JALR = 0b111

    @property
    def mnemonic(self):
        return self.name.lower().replace("op_", "")

    @property
    def to_str(self):
        return f"{self.value:#05b}"