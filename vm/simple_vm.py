from codegenerator.intermediate_code import TACInstruction, Label, IntermediateCode
from typing import Dict, List, Any, Optional

class SimpleVM:
    def __init__(self, debug=False):
        self.global_memory: Dict[str, Any] = {}
        self.frames: List[Dict[str, Any]] = [{}]  # 初始帧为全局帧
        self.pc: int = 0
        self.label_map: Dict[str, int] = {}
        self.value_stack: List[Any] = []
        self.return_stack: List[int] = []
        self.call_result_stack: List[Optional[str]] = []
        self.function_params: Dict[str, List[str]] = {}
        self.library_functions = {
            'print': self._lib_print,
            'input': self._lib_input,
        }
        self.debug = debug
        self.arrays = {}  # 用于存储数组数据
        self.tuples = {}  # 用于存储元组数据

    def __str__(self):
        return (
            f"SimpleVM("
            f"global_memory={self.global_memory}, "
            f"frames={self.frames}, "
            f"pc={self.pc}, "
            f"value_stack={self.value_stack}, "
            f"return_stack={self.return_stack}, "
            f"call_result_stack={self.call_result_stack})"
        )

    def load_program(self, code: IntermediateCode):
        self.instructions = code.instructions
        for index, instr in enumerate(self.instructions):
            if isinstance(instr, Label):
                self.label_map[instr.name] = index
                if hasattr(instr, 'params'):
                    self.function_params[instr.name] = instr.params
        if "main" in self.label_map:
            self.pc = self.label_map["main"]

    def get_value(self, operand: Optional[str]) -> Any:
        if operand is None:
            return None
        if operand.startswith('"') or operand.startswith("'"):
            return operand[1:-1]
        try:
            return int(operand)
        except ValueError:
            pass
        try:
            return float(operand)
        except ValueError:
            pass
        
        # 先检查当前帧
        if self.frames:
            value = self.frames[-1].get(operand)
            if value is not None:
                return value
            
        # 再检查全局内存
        value = self.global_memory.get(operand)
        if value is not None:
            return value
        
        raise ValueError(f"未定义的变量: {operand}")

    def execute(self) -> Any:
        while 0 <= self.pc < len(self.instructions):
            old_pc = self.pc
            instr = self.instructions[self.pc]
            if self.debug:
                print("执行指令:", instr, self.value_stack)
            if isinstance(instr, Label):
                self.pc += 1
                continue
            result = self.execute_instruction(instr)
            if result is not None:
                # 主函数返回时直接返回结果
                return result
            if self.pc == old_pc:
                self.pc += 1

    def execute_instruction(self, instr: TACInstruction) -> Optional[Any]:
        if instr.opcode == 'param':
            value = self.get_value(instr.arg1)
            self.value_stack.append(value)
            if self.debug:
                print(f"DEBUG: param {instr.arg1}={value}, stack={self.value_stack}")

        elif instr.opcode == 'call':
            if instr.arg1 in self.library_functions:
                if self.debug:
                    print(f"DEBUG: library call {instr.arg1} with {instr.arg2} params, stack={self.value_stack}")
                param_count = int(instr.arg2)
                params = []
                for _ in range(param_count):
                    params.insert(0, self.value_stack.pop())
                result = self.library_functions[instr.arg1](params)
                self.value_stack.clear()
                if result is not None and instr.result:
                    if self.frames:
                        self.frames[-1][instr.result] = result
                    else:
                        self.global_memory[instr.result] = result
                self.pc += 1
                return None

            if self.debug:
                print(f"DEBUG: call {instr.arg1} with {instr.arg2} params, stack={self.value_stack}")
            self.return_stack.append(self.pc + 1)
            self.call_result_stack.append(instr.result)
            new_frame = {}
            param_count = int(instr.arg2)
            params = []
            for _ in range(param_count):
                params.insert(0, self.value_stack.pop())
            self.value_stack.clear()
            func_name = instr.arg1
            param_names = self.function_params.get(func_name, [])
            for i, value in enumerate(params):
                if i < len(param_names):
                    new_frame[param_names[i]] = value
            self.frames.append(new_frame)
            self.pc = self.label_map[func_name]
            return

        elif instr.opcode == 'return':
            return_value = self.get_value(instr.arg1)
            if self.debug:
                print(f"DEBUG: return {return_value}, frames={self.frames}")
            if self.return_stack:
                self.frames.pop()
                self.pc = self.return_stack.pop()
                if self.frames and self.call_result_stack:
                    result_var = self.call_result_stack.pop()
                    if result_var:
                        self.frames[-1][result_var] = return_value
                self.value_stack.clear()
                self.value_stack.append(return_value)
                return 
            else:
                return return_value

        # 算术与比较运算
        if instr.opcode in {'+', '-', '*', '/', '%', '>', '<', '>=', '<=', '==', '!='}:
            left = self.get_value(instr.arg1)
            right = self.get_value(instr.arg2)
            if left is None or right is None:
                raise ValueError(f"无效的操作数: {instr.arg1}({left}) {instr.opcode} {instr.arg2}({right})")
            if self.debug:
                if instr.opcode in {'+', '-', '*', '/', '%'}:
                    print(f"DEBUG: 算术运算: {left} {instr.opcode} {right}")
                else:
                    print(f"DEBUG: 比较运算: {left} {instr.opcode} {right}")
            if instr.opcode == '+':
                value = left + right
            elif instr.opcode == '-':
                value = left - right
            elif instr.opcode == '*':
                value = left * right
            elif instr.opcode == '/':
                value = left / right
            elif instr.opcode == '%':
                value = left % right
            elif instr.opcode == '>':
                value = right < left
            elif instr.opcode == '<':
                value = right > left
            elif instr.opcode == '>=':
                value = right <= left
            elif instr.opcode == '<=':
                value = right >= left
            elif instr.opcode == '==':
                value = right != left
            elif instr.opcode == '!=':
                value = right == left
            if self.frames:
                self.frames[-1][instr.result] = value
            else:
                self.global_memory[instr.result] = value

        elif instr.opcode == 'goto':
            if self.debug:
                print(f"DEBUG: goto {instr.arg1}")
            self.pc = self.label_map[instr.arg1]
            return

        elif instr.opcode == 'if_goto':
            condition = self.get_value(instr.arg1)
            if self.debug:
                print(f"DEBUG: if_goto condition={condition}, target={instr.arg2}")
            if condition:
                self.pc = self.label_map[instr.arg2]
                return

        elif instr.opcode == 'assign':
            value = self.get_value(instr.arg1)
            if self.debug:
                print(f"DEBUG: assign {instr.result} = {value}")
            if self.frames:
                self.frames[-1][instr.result] = value
            else:
                self.global_memory[instr.result] = value

        # 处理数组分配
        elif instr.opcode == 'alloc_array':
            size = int(self.get_value(instr.arg1))
            array_id = instr.result
            self.arrays[array_id] = [None] * size
            if self.frames:
                self.frames[-1][array_id] = array_id
            else:
                self.global_memory[array_id] = array_id
                
        # 处理数组存储
        elif instr.opcode == 'array_store':
            array_id = self.get_value(instr.arg1)
            # 从 arg2 中解析出索引和值
            index_str, value_str = instr.arg2.split(',')
            index = int(self.get_value(index_str))
            value = self.get_value(value_str)
            
            if array_id not in self.arrays:
                raise ValueError(f"未定义的数组: {array_id}")
            if not 0 <= index < len(self.arrays[array_id]):
                raise IndexError(f"数组索引越界: {index}")
            self.arrays[array_id][index] = value
            
        # 处理数组/元组加载
        elif instr.opcode == 'array_load':
            array_id = self.get_value(instr.arg1)
            index = int(self.get_value(instr.arg2))
            
            # 先检查是否是元组
            if array_id in self.tuples:
                if not 0 <= index < len(self.tuples[array_id]):
                    raise IndexError(f"元组索引越界: {index}")
                value = self.tuples[array_id][index]
            # 再检查是否是数组
            elif array_id in self.arrays:
                if not 0 <= index < len(self.arrays[array_id]):
                    raise IndexError(f"数组索引越界: {index}")
                value = self.arrays[array_id][index]
            else:
                raise ValueError(f"未定义的数组/元组: {array_id}")
            
            if self.frames:
                self.frames[-1][instr.result] = value
            else:
                self.global_memory[instr.result] = value

        # 处理元组分配
        elif instr.opcode == 'alloc_tuple':
            size = int(self.get_value(instr.arg1))
            tuple_id = instr.result
            self.tuples[tuple_id] = [None] * size
            # 将元组ID存储到当前帧或全局内存
            if self.frames:
                self.frames[-1][tuple_id] = tuple_id
            else:
                self.global_memory[tuple_id] = tuple_id
            
        # 处理元组存储
        elif instr.opcode == 'tuple_store':
            tuple_id = self.get_value(instr.arg1)
            # 从 arg2 中解析出索引和值
            index_str, value_str = instr.arg2.split(',')
            index = int(self.get_value(index_str))
            value = self.get_value(value_str)
            
            if tuple_id not in self.tuples:
                raise ValueError(f"未定义的元组: {tuple_id}")
            if not 0 <= index < len(self.tuples[tuple_id]):
                raise IndexError(f"元组索引越界: {index}")
            if self.tuples[tuple_id][index] is not None:
                raise ValueError(f"元组元素不可修改: {tuple_id}[{index}]")
            self.tuples[tuple_id][index] = value
            
        # 处理元组加载
        elif instr.opcode == 'tuple_load':
            tuple_id = self.get_value(instr.arg1)
            index = int(self.get_value(instr.arg2))
            if tuple_id not in self.tuples:
                raise ValueError(f"未定义的元组: {tuple_id}")
            if not 0 <= index < len(self.tuples[tuple_id]):
                raise IndexError(f"元组索引越界: {index}")
            value = self.tuples[tuple_id][index]
            # 将加载的值存储到结果变量
            if self.frames:
                self.frames[-1][instr.result] = value
            else:
                self.global_memory[instr.result] = value

        return None

    def _lib_print(self, args):
        if args:
            format_string = args[0]
            if isinstance(format_string,str):
                format_string=format_string.replace("\\",'\n')
                values = args[1:]
                print(format_string.format(*values),end='')
            else:
                print(*args)
        else:
            print()


    def _lib_input(self, args):
        prompt = args[0] if args else ""
        return input(prompt)

def run_tac_program(code: IntermediateCode, debug=False) -> Any:
    vm = SimpleVM(debug=debug)
    vm.load_program(code)
    return vm.execute()

