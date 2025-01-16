from intermediate_code import TACInstruction, Label, IntermediateCode
from ast_nodes import *
from typing import Dict, Optional

class LoopContext:
    """用于保存当前循环的 start_label (或 update_label) 和 end_label。"""
    def __init__(self, start_label: str, end_label: str):
        self.start_label = start_label
        self.end_label = end_label

class CodeGenerator:
    def __init__(self):
        self.code = IntermediateCode(instructions=[])
        self.temp_count = 0
        self.label_count = 0

        self.symbol_table: Dict[str, str] = {}  # 变量 -> 其地址
        self.function_stack = []               # 当前函数名栈
        self.loop_stack = []                   # 嵌套循环的上下文栈

        self.has_return = False                # 是否出现过return语句

    def new_temp(self) -> str:
        temp_name = f"t{self.temp_count}"
        self.temp_count += 1
        return temp_name

    def new_label(self) -> str:
        label_name = f"L{self.label_count}"
        self.label_count += 1
        return label_name

    def generate(self, node: ASTNode) -> IntermediateCode:
        """对整个AST进行代码生成"""
        self.visit(node)
        return self.code

    def visit(self, node: ASTNode) -> Optional[str]:
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> Optional[str]:
        raise Exception(f"No visit_{type(node).__name__} method defined")

    # ============== Program ==============
    def visit_Program(self, node: Program) -> Optional[str]:
        """
        在最终生成的中间代码里：
        1. 先生成全局(非函数)声明
        2. 然后生成 main 函数(若存在)
        3. 最后生成其他函数
        """
        global_decls = []
        main_decl = None
        other_funcs = []

        # 1) 分分类
        for decl in node.declarations:
            if isinstance(decl, FunctionDecl):
                if decl.name == "main":
                    main_decl = decl
                else:
                    other_funcs.append(decl)
            else:
                # 非函数声明, 如 VarDecl / ImportStatement 等
                global_decls.append(decl)

        # 2) 先 visit 所有全局声明
        for g in global_decls:
            self.visit(g)

        # 3) 再 visit main 函数
        if main_decl is not None:
            self.visit(main_decl)

        # 4) 最后 visit 其他函数
        for f in other_funcs:
            self.visit(f)

        return None

    # ============== ImportStatement ==============
    def visit_ImportStatement(self, node: ImportStatement) -> Optional[str]:
        # 可以忽略或用于记录导入信息
        return None

    # ============== FunctionDecl ==============
    def visit_FunctionDecl(self, node: FunctionDecl) -> Optional[str]:
        # 生成函数标签
        func_label = Label(name=node.name)
        func_label.params = [param.name for param in node.params]  # 记录形参名称
        self.code.add_instruction(func_label)

        # 入栈当前函数名，并重置 has_return
        self.function_stack.append(node.name)
        self.has_return = False

        # 函数参数 - 直接使用参数名称
        for param in node.params:
            self.symbol_table[param.name] = param.name  # 使用原始参数名

        # 访问函数体
        self.visit(node.body)

        # 若函数返回类型不为 nil 并且尚未出现 return，则补一个空return
        if node.return_type != 'nil' and not self.has_return:
            self.code.add_instruction(TACInstruction(opcode='return', arg1=None))

        # 清理函数参数
        for param in node.params:
            self.symbol_table.pop(param.name, None)

        # 出栈
        self.function_stack.pop()
        return None

    # ============== CompoundStmt ==============
    def visit_CompoundStmt(self, node: CompoundStmt) -> Optional[str]:
        for stmt in node.statements:
            self.visit(stmt)
        return None

    # ============== VarDecl ==============
    def visit_VarDecl(self, node: VarDecl) -> Optional[str]:
        var_name = node.name
        self.symbol_table[var_name] = var_name
        if node.init_value:
            value = self.visit(node.init_value)
            instr = TACInstruction(opcode='assign', arg1=value, result=var_name)
            self.code.add_instruction(instr)
        return None

    # ============== Assignment ==============
    def visit_Assignment(self, node: Assignment) -> Optional[str]:
        value = self.visit(node.value)
        
        # 如果是索引赋值
        if isinstance(node.target, IndexAccess):
            collection_val = self.visit(node.target.collection)
            index_val = self.visit(node.target.index)
            
            # 检查是否是元组赋值（不允许）
            if hasattr(node.target, 'collection_type') and node.target.collection_type == 'tuple':
                raise Exception("Cannot modify tuple elements")
            
            # 数组赋值
            self.code.add_instruction(TACInstruction(
                opcode='array_store',
                arg1=collection_val,
                arg2=f"{index_val},{value}",
                result=None
            ))
            return None
        
        # 普通变量赋值
        target = self.visit(node.target)
        self.code.add_instruction(TACInstruction(
            opcode='assign',
            arg1=value,
            result=target
        ))
        return target

    # ============== ReturnStmt ==============
    def visit_ReturnStmt(self, node: ReturnStmt) -> Optional[str]:
        self.has_return = True
        ret_val = ""
        if node.expr:
            ret_val = self.visit(node.expr)
        instr = TACInstruction(opcode='return', arg1=ret_val if ret_val else None)
        self.code.add_instruction(instr)
        return None

    # ============== ExpressionStmt ==============
    def visit_ExpressionStmt(self, node: ExpressionStmt) -> Optional[str]:
        return self.visit(node.expression)

    # ============== Comment ==============
    def visit_Comment(self, node: Comment) -> Optional[str]:
        # 注释可忽略或用作后续调试
        return None

    # ============== BinaryOp ==============
    def visit_BinaryOp(self, node: BinaryOp) -> Optional[str]:
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        
        # 对于比较运算符，需要反转操作符
        op_map = {
            '<=': '>',
            '>=': '<',
            '<': '>=',
            '>': '<=',
            '==': '!=',
            '!=': '=='
        }
        
        if (node.operator in op_map):
            instr = TACInstruction(opcode=op_map[node.operator], arg1=right, arg2=left, result=temp)
        else:
            instr = TACInstruction(opcode=node.operator, arg1=left, arg2=right, result=temp)
        
        self.code.add_instruction(instr)
        return temp

    # ============== UnaryOp ==============
    def visit_UnaryOp(self, node: UnaryOp) -> Optional[str]:
        if node.operator in ['++', '--']:
            # 获取操作数
            var = self.visit(node.operand)
            temp = self.new_temp()
            
            # 先执行自增/自减运算
            if node.operator == '++':
                self.code.add_instruction(TACInstruction(
                    opcode='+',
                    arg1=var,
                    arg2='1',
                    result=var
                ))
            else:  # --
                self.code.add_instruction(TACInstruction(
                    opcode='-',
                    arg1=var,
                    arg2='1',
                    result=var
                ))

            # 然后将新值存入临时变量
            self.code.add_instruction(TACInstruction(
                opcode='assign',
                arg1=var,
                result=temp
            ))
            return temp

        operand = self.visit(node.operand)
        temp = self.new_temp()
        instr = TACInstruction(opcode=node.operator, arg1=operand, result=temp)
        self.code.add_instruction(instr)
        return temp

    # ============== Literal ==============
    def visit_Literal(self, node: Literal) -> Optional[str]:
        if node.type == 'str':
            return f"\"{node.value}\""
        if node.type == 'char':
            return f"'{node.value}'"
        return str(node.value)

    # ============== Variable ==============
    def visit_Variable(self, node: Variable) -> Optional[str]:
        var_name = node.name
        if (var_name not in self.symbol_table):
            raise Exception(f"Undefined variable '{var_name}'")
        return var_name

    # ============== FunctionCall ==============
    def visit_FunctionCall(self, node: FunctionCall) -> Optional[str]:
        """生成函数调用的三地址码，确保嵌套调用按正确顺序执行"""
        # 先递归处理所有参数，确保内层函数调用先执行
        arg_temps = []
        
        # 从右到左处理参数，确保嵌套调用正确执行
        for arg in reversed(node.arguments):
            arg_val = self.visit(arg)
            arg_temps.append(arg_val)
        
        # 生成参数传递指令 - 需要反转回来，因为我们要先传左边的参数
        for arg_val in reversed(arg_temps):  # 反转回来，恢复从左到右的顺序
            self.code.add_instruction(TACInstruction(
                opcode='param',
                arg1=arg_val
            ))
        
        # 生成函数调用指令
        temp = self.new_temp()
        self.code.add_instruction(TACInstruction(
            opcode='call',
            arg1=node.name,
            arg2=str(len(arg_temps)),
            result=temp
        ))
        
        return temp

    # ============== IfStmt ==============
    def visit_IfStmt(self, node: IfStmt) -> Optional[str]:
        """生成 if 语句的三地址码
        t1 = condition
        if t1 goto L1  # 条件为真时跳转到 L1
        false_body     # 条件为假时的代码
        goto L2
        Label L1:
        true_body      # 条件为真时的代码
        Label L2:
        """
        # 计算条件表达式
        cond = self.visit(node.condition)
        
        # 创建标签
        true_label = self.new_label()   # 获取标签名
        end_label = self.new_label()    # 获取标签名
        
        # 生成条件跳转指令
        self.code.add_instruction(TACInstruction(
            opcode='if_goto',
            arg1=cond,
            arg2=true_label  # 直接使用标签名字符串
        ))
        
        # 生成 else 分支的代码（条件为假时执行）
        if node.else_branch:
            self.visit(node.else_branch)
        
        # 跳过 true 分支
        self.code.add_instruction(TACInstruction(
            opcode='goto',
            arg1=end_label  # 直接使用标签名字符串
        ))
        
        # 生成 true 分支的代码
        self.code.add_instruction(Label(name=true_label))  # 创建 Label 对象
        self.visit(node.then_branch)
        
        # if 语句结束
        self.code.add_instruction(Label(name=end_label))  # 创建 Label 对象
        
        return None

    # ============== ElifBranch ==============
    def visit_ElifBranch(self, node: ElifBranch) -> Optional[str]:
        cond_label = self.new_label()
        end_label = self.new_label()

        cond = self.visit(node.condition)
        self.code.add_instruction(TACInstruction(opcode='if_goto', arg1=cond, arg2=cond_label))

        # then body
        self.visit(node.body)

        self.code.add_instruction(TACInstruction(opcode='goto', arg1=end_label))
        self.code.add_instruction(Label(name=cond_label))
        self.code.add_instruction(Label(name=end_label))
        return None

    # ============== ForStmt ==============
    def visit_ForStmt(self, node: ForStmt) -> Optional[str]:
        start_label = self.new_label()  # 循环开始标签
        end_label = self.new_label()    # 循环结束标签
        update_label = self.new_label() # 更新标签

        # 为break/continue保存上下文
        self.loop_stack.append(LoopContext(update_label, end_label))

        # initializer
        if node.initializer:
            self.visit(node.initializer)

        # start_label
        self.code.add_instruction(Label(name=start_label))

        # condition - 需要生成退出条件
        if node.condition:
            # 对于 i <= 10，我们需要生成 i > 10 作为退出条件
            if isinstance(node.condition, BinaryOp):
                # 反转比较运算符
                op_map = {
                    '<=': '>',
                    '>=': '<',
                    '<': '>=',
                    '>': '<=',
                    '==': '!=',
                    '!=': '=='
                }
                # 交换左右操作数并反转操作符
                if node.condition.operator in op_map:
                    temp = self.new_temp()
                    self.code.add_instruction(TACInstruction(
                        opcode=op_map[node.condition.operator],
                        arg1=self.visit(node.condition.left),  # 保持原始顺序
                        arg2=self.visit(node.condition.right),
                        result=temp
                    ))
                    cond_val = temp
                else:
                    cond_val = self.visit(node.condition)
            else:
                cond_val = self.visit(node.condition)
            
            # 当条件为真时跳转到循环结束
            self.code.add_instruction(TACInstruction(
                opcode='if_goto',
                arg1=cond_val,
                arg2=end_label
            ))

        # body
        self.visit(node.body)

        # update label
        self.code.add_instruction(Label(name=update_label))
        
        # update
        if node.update:
            self.visit(node.update)

        # 跳回循环开始处
        self.code.add_instruction(TACInstruction(
            opcode='goto',
            arg1=start_label
        ))

        # 循环结束
        self.code.add_instruction(Label(name=end_label))

        self.loop_stack.pop()
        return None

    # ============== BreakStmt ==============
    def visit_BreakStmt(self, node: BreakStmt) -> Optional[str]:
        if not self.loop_stack:
            raise Exception("break statement not in loop")
        # 跳转到当前循环的 end_label
        end_label = self.loop_stack[-1].end_label
        self.code.add_instruction(TACInstruction(opcode='goto', arg1=end_label))
        return None

    # ============== ContinueStmt ==============
    def visit_ContinueStmt(self, node: ContinueStmt) -> Optional[str]:
        if not self.loop_stack:
            raise Exception("continue statement not in loop")
        # 跳转回当前循环的 start_label（或 update_label）。
        # 在此示例中，我们简单地使用 start_label
        start_label = self.loop_stack[-1].start_label
        self.code.add_instruction(TACInstruction(opcode='goto', arg1=start_label))
        return None

    # ============== ArrayAccess ==============
    def visit_ArrayAccess(self, node: ArrayAccess) -> Optional[str]:
        array_val = self.visit(node.array)
        index_val = self.visit(node.index)
        temp = self.new_temp()
        instr = TACInstruction(opcode='index_access', arg1=array_val, arg2=index_val, result=temp)
        self.code.add_instruction(instr)
        return temp

    # ============== ListLiteral ==============
    def visit_ListLiteral(self, node: ListLiteral) -> Optional[str]:
        # 1. 创建一个临时变量存储列表
        list_var = self.new_temp()
        
        # 2. 生成分配空间的指令
        size = len(node.elements)
        self.code.add_instruction(TACInstruction(
            opcode='alloc_array',
            arg1=str(size),
            result=list_var
        ))
        
        # 3. 初始化每个元素
        for i, elem in enumerate(node.elements):
            elem_val = self.visit(elem)
            self.code.add_instruction(TACInstruction(
                opcode='array_store',
                arg1=list_var,
                arg2=f"{str(i)},{elem_val}",
                result=None
            ))
        
        return list_var

    # ============== TupleLiteral ==============
    def visit_TupleLiteral(self, node: TupleLiteral) -> Optional[str]:
        # 1. 创建一个临时变量存储元组
        tuple_var = self.new_temp()
        
        # 2. 生成分配空间的指令
        size = len(node.elements)
        self.code.add_instruction(TACInstruction(
            opcode='alloc_tuple',
            arg1=str(size),
            result=tuple_var
        ))
        
        # 3. 初始化每个元素
        for i, elem in enumerate(node.elements):
            elem_val = self.visit(elem)
            self.code.add_instruction(TACInstruction(
                opcode='tuple_store',
                arg1=tuple_var,
                arg2=f"{str(i)},{elem_val}",
                result=None
            ))
        
        return tuple_var

    # ============== IndexAccess ==============
    def visit_IndexAccess(self, node: IndexAccess) -> Optional[str]:
        # 1. 获取集合和索引值
        collection_val = self.visit(node.collection)
        index_val = self.visit(node.index)
        
        # 2. 创建临时变量存储访问结果
        temp = self.new_temp()
        
        # 3. 生成访问指令
        # 检查变量名是否在元组存储中
        if collection_val in self.symbol_table and collection_val.startswith('t') and collection_val in [instr.result for instr in self.code.instructions if instr.opcode == 'alloc_tuple']:
            self.code.add_instruction(TACInstruction(
                opcode='tuple_load',
                arg1=collection_val,
                arg2=index_val,
                result=temp
            ))
        else:  # 数组访问
            self.code.add_instruction(TACInstruction(
                opcode='array_load',
                arg1=collection_val,
                arg2=index_val,
                result=temp
            ))
        
        return temp
