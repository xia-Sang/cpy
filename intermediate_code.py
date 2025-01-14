from dataclasses import dataclass
from typing import Optional, List, Union

@dataclass
class Label:
    name: str

@dataclass
class TACInstruction:
    def __init__(self, opcode: str, arg1: Optional[str] = None, 
                 arg2: Optional[str] = None, arg3: Optional[str] = None,
                 result: Optional[str] = None):
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3
        self.result = result

    def __str__(self):
        # 根据操作码（opcode）类型，生成不同格式的字符串
        if self.opcode == 'goto':
            return f"goto {self.arg1}"
        elif self.opcode == 'if_goto':
            return f"if {self.arg1} goto {self.arg2}"
        elif self.opcode == 'label':
            return f"{self.arg1}:"
        elif self.opcode == 'return':
            return f"return {self.arg1}" if self.arg1 else "return"
        elif self.opcode == 'print':
            return f"print {self.arg1}"
        elif self.opcode == 'param':
            return f"param {self.arg1}"
        elif self.opcode == 'call':
            return f"{self.result} = call {self.arg1}, {self.arg2}"
        elif self.opcode == 'assign':
            return f"{self.result} = {self.arg1}"
        elif self.opcode == 'alloc_array' or self.opcode == 'alloc_tuple':
            return f"{self.result} = new {self.opcode[6:]}[{self.arg1}]"
        elif self.opcode == 'array_store' or self.opcode == 'tuple_store':
            # 从 arg2 中分离索引和值
            index, value = self.arg2.split(',')
            collection_type = 'array' if self.opcode == 'array_store' else 'tuple'
            return f"{collection_type}_store {self.arg1}[{index}] = {value}"
        elif self.opcode == 'array_load' or self.opcode == 'tuple_load':
            return f"{self.result} = {self.arg1}[{self.arg2}]"
        else:
            # Binary or unary operations
            return f"{self.result} = {self.arg1} {self.opcode} {self.arg2}"

@dataclass
class IntermediateCode:
    instructions: List[Union[TACInstruction, Label]]

    def add_instruction(self, instruction: Union[TACInstruction, Label]):
        self.instructions.append(instruction)

    def __str__(self):
        return "\n".join(str(instr) for instr in self.instructions)
