class CPU:
    def __init__(self):
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.sp = 7
        self.flag = 0
        self.register[self.sp] = 0xF4  # 244 decimal
        self.running = True
        self.dispatch = {}
        self.dispatch[1] = self.HLT		# 0b00000001
        self.dispatch[17] = self.RET  # 0b00010001
        self.dispatch[69] = self.PUSH  # 01000101
        self.dispatch[70] = self.POP  # 01000110
        self.dispatch[71] = self.PRN  # 0b01000111
        self.dispatch[80] = self.CALL  # 0b01010000
        self.dispatch[84] = self.JMP  # 0b01010100
        self.dispatch[85] = self.JEQ  # 0b01010101
        self.dispatch[86] = self.JNE  # 0b01010110
        self.dispatch[130] = self.LDI  # 0b10000010

    def load(self, program_filename):
        address = 0

        with open(program_filename) as f:
            for line in f:
                line = line.split('#')
                line = line[0].strip()

                if line == '':
                    continue

                self.ram_write(address, int(line, 2))

                address += 1

    def HLT(self, operand_a=None, operand_b=None):
        self.running = False

    def RET(self, operand_a=None, operand_b=None):
        return_addr = self.ram_read(self.register[self.sp])
        self.register[self.sp] += 1
        self.pc = return_addr

    def PUSH(self, operand_a, operand_b=None):
        self.register[self.sp] -= 1
        value = self.register[operand_a]
        address = self.register[self.sp]
        self.ram_write(address, value)

    def POP(self, operand_a, operand_b=None):
        value = self.ram_read(self.register[self.sp])
        self.register[operand_a] = value
        self.register[self.sp] += 1

    def PRN(self, operand_a, operand_b=None):
        print("Print Value: ", self.register[operand_a])

    def CALL(self, operand_a, operand_b=None):
        return_addr = self.pc + 2
        self.register[self.sp] -= 1
        self.ram_write(self.register[self.sp], return_addr)
        dest_addr = self.register[operand_a]
        self.pc = dest_addr

    def JMP(self, operand_a, operand_b=None):
        self.pc = self.register[operand_a]

    def JEQ(self, operand_a, operand_b=None):
        if self.flag == 1:
            self.pc = self.register[operand_a]
        else:
            self.pc += 2

    def JNE(self, operand_a, operand_b=None):
        if self.flag != 1:
            self.pc = self.register[operand_a]
        else:
            self.pc += 2

    def LDI(self, operand_a, operand_b):
        self.register[operand_a] = operand_b

    def alu(self, op, reg_a, reg_b):
        # ADD
        if op == 160:
            self.register[reg_a] += self.register[reg_b]
        # SUB
        elif op == 161:
            self.register[reg_a] -= self.register[reg_b]
        # MUL
        elif op == 162:
            self.register[reg_a] *= self.register[reg_b]
        # DIV
        elif op == 163:
            self.register[reg_a] /= self.register[reg_b]
        # CMP
        elif op == 167:
            if self.register[reg_a] == self.register[reg_b]:
                self.flag = 0b00000001
            elif self.register[reg_a] > self.register[reg_b]:
                self.flag = 0b00000010
            elif self.register[reg_a] < self.register[reg_b]:
                self.flag = 0b00000100
            else:
                self.flag = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE --> PC: %02i | RAM: %03i %03i %03i | Register:" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02i" % self.register[i], end='')

        print(" | Stack:", end='')

        for i in range(236, 244):
            print(" %02i" % self.ram_read(i), end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def run(self):
        while self.running:
            instruction = self.ram_read(self.pc)
            inst_len = ((instruction & 0b11000000) >> 6) + 1
            use_alu = ((instruction & 0b00100000) >> 5)
            pc_setter = ((instruction & 0b00010000) >> 4)

            if inst_len >= 1:
                operand_a = self.ram_read(self.pc + 1)

            if inst_len >= 2:
                operand_b = self.ram_read(self.pc + 2)

            if use_alu:
                self.alu(instruction, operand_a, operand_b)
                self.pc += inst_len
                # self.trace()

            elif pc_setter:
                self.dispatch[instruction](operand_a, operand_b)
                # self.trace()

            elif self.dispatch.get(instruction):
                self.dispatch[instruction](operand_a, operand_b)
                self.pc += inst_len
                # self.trace()

            else:
                print("Unknown instruction")
                self.running = False
