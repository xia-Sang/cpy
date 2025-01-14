from typ import Type, ListType, TupleType
from symbol import Symbol, SymbolTable
from ast_nodes import *
import sys

class SemanticError(Exception):
    """语义错误异常"""
    def __init__(self, message: str, node: ASTNode):
        self.message = message
        self.node = node
        super().__init__(f"Semantic error: {message} at node {type(node).__name__}({node})")

class SemanticAnalyzer:
    """语义分析器，使用访问者模式遍历AST"""
    def __init__(self):
        self.global_scope = SymbolTable()
        self.current_scope = self.global_scope
        self.current_function: Optional[Symbol] = None  # 当前正在分析的函数
        
        # 初始化库函数
        self.library_functions = {
            'print': FunctionDecl(
                return_type='void',
                name='print',
                params=[],  # 空参数列表表示可变参数
                body=CompoundStmt(statements=[])  # 空实现，实际执行由虚拟机处理
            ),
            'input': FunctionDecl(
                return_type='str',
                name='input',
                params=[Parameter(type='str', name='prompt')],
                body=CompoundStmt(statements=[])  # 空实现，实际执行由虚拟机处理
            )
        }
        
        # 将库函数添加到全局作用域
        for func in self.library_functions.values():
            # 解析函数返回类型
            return_type = self.resolve_type(func.return_type)
            # 解析参数类型
            params = []
            for param in func.params:
                param_type = self.resolve_type(param.type)
                params.append((param.name, param_type))
            
            # 定义函数符号
            func_symbol = Symbol(
                name=func.name,
                symbol_type='function',
                data_type=return_type,
                is_function=True,
                params=params,
                is_variadic=func.name == 'print'  # print 函数是可变参数
            )
            self.global_scope.define(func_symbol)

    def analyze(self, node: ASTNode):
        """开始语义分析"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        """默认的访问方法，递归访问子节点"""
        for field, value in vars(node).items():
            if isinstance(value, ASTNode):
                self.analyze(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ASTNode):
                        self.analyze(item)

    def visit_Program(self, node: Program):
        for decl in node.declarations:
            self.analyze(decl)

    def visit_ClassDecl(self, node: ClassDecl):
        # 定义类符号
        class_symbol = Symbol(
            name=node.name,
            symbol_type='class',
            data_type=Type(node.name)  # 类名作为类型名
        )
        if self.current_scope.lookup(node.name):
            raise SemanticError(f"Class '{node.name}' already defined.", node)
        self.current_scope.define(class_symbol)

        # 创建新作用域用于类成员
        self.current_scope = SymbolTable(parent=self.current_scope)
        # 处理继承（暂时忽略继承的语义检查）
        # 未来可以检查父类是否存在等

        # 分析类成员
        for member in node.members:
            self.analyze(member)

        # 恢复作用域
        self.current_scope = self.current_scope.parent

    def visit_MemberFunctionDecl(self, node: MemberFunctionDecl):
        # 解析方法的返回类型
        return_type = self.resolve_type(node.return_type)
        # 解析参数类型
        params = []
        for param in node.params:
            param_type = self.resolve_type(param.type)
            params.append( (param.name, param_type) )

        # 定义方法符号
        func_symbol = Symbol(
            name=node.name,
            symbol_type='function',
            data_type=return_type,
            is_function=True,
            params=params
        )
        if self.current_scope.lookup(node.name):
            raise SemanticError(f"Function '{node.name}' already defined in current scope.", node)
        self.current_scope.define(func_symbol)

        # 设置当前函数上下文
        enclosing_function = self.current_function
        self.current_function = func_symbol

        # 创建新作用域
        self.current_scope = SymbolTable(parent=self.current_scope)
        # 定义参数为变量
        for param_name, param_type in params:
            var_symbol = Symbol(
                name=param_name,
                symbol_type='variable',
                data_type=param_type
            )
            self.current_scope.define(var_symbol)

        # 分析函数体
        self.analyze(node.body)

        # 恢复作用域和函数上下文
        self.current_scope = self.current_scope.parent
        self.current_function = enclosing_function

    def visit_FunctionDecl(self, node: FunctionDecl):
        # 处理全局或顶层函数，逻辑与 MemberFunctionDecl 类似
        # 解析函数返回类型
        return_type = self.resolve_type(node.return_type)
        # 解析参数类型
        params = []
        for param in node.params:
            param_type = self.resolve_type(param.type)
            params.append( (param.name, param_type) )

        # 定义函数符号
        func_symbol = Symbol(
            name=node.name,
            symbol_type='function',
            data_type=return_type,
            is_function=True,
            params=params
        )
        if self.current_scope.lookup(node.name):
            raise SemanticError(f"Function '{node.name}' already defined in current scope.", node)
        self.current_scope.define(func_symbol)

        # 设置当前函数上下文
        enclosing_function = self.current_function
        self.current_function = func_symbol

        # 创建新作用域
        self.current_scope = SymbolTable(parent=self.current_scope)
        # 定义参数为变量
        for param_name, param_type in params:
            var_symbol = Symbol(
                name=param_name,
                symbol_type='variable',
                data_type=param_type
            )
            self.current_scope.define(var_symbol)

        # 分析函数体
        self.analyze(node.body)

        # 恢复作用域和函数上下文
        self.current_scope = self.current_scope.parent
        self.current_function = enclosing_function

    def visit_CompoundStmt(self, node: CompoundStmt):
        # 创建新作用域
        self.current_scope = SymbolTable(parent=self.current_scope)
        for stmt in node.statements:
            self.analyze(stmt)
        # 恢复作用域
        self.current_scope = self.current_scope.parent

    def visit_VarDecl(self, node: VarDecl):
        var_type = self.resolve_type(node.var_type)
        # 定义变量符号
        var_symbol = Symbol(
            name=node.name,
            symbol_type='variable',
            data_type=var_type
        )
        if self.current_scope.lookup(node.name):
            raise SemanticError(f"Variable '{node.name}' already defined in current scope.", node)
        self.current_scope.define(var_symbol)
        # 如果有初始化值，检查类型
        if node.init_value:
            init_type = self.analyze(node.init_value)
            if not self.type_compatible(var_type, init_type):
                raise SemanticError(f"Type mismatch in variable initialization: expected '{var_type.name}', got '{init_type.name}'.", node)

    def visit_Assignment(self, node: Assignment):
        # 分析赋值目标
        target_type = self.analyze(node.target)
        # 分析赋值值
        value_type = self.analyze(node.value)
        # 检查类型兼容性
        if not self.type_compatible(target_type, value_type):
            raise SemanticError(f"Type mismatch in assignment: expected '{target_type.name}', got '{value_type.name}'.", node)
        # 特别处理元组的不可变性
        if isinstance(node.target, IndexAccess):
            collection_type = self.analyze(node.target.collection)
            if isinstance(collection_type, TupleType):
                raise SemanticError("Tuples are immutable and cannot be assigned to.", node)

    def visit_ReturnStmt(self, node: ReturnStmt):
        # 确保在函数内部
        if not self.current_function:
            raise SemanticError("Return statement outside of function.", node)
        # 获取当前函数的返回类型
        return_type = self.current_function.data_type
        if node.expr:
            expr_type = self.analyze(node.expr)
            if not self.type_compatible(return_type, expr_type):
                raise SemanticError(f"Return type mismatch: expected '{return_type.name}', got '{expr_type.name}'.", node)
        else:
            if return_type.name != 'void':
                raise SemanticError(f"Return type mismatch: expected '{return_type.name}', got 'void'.", node)

    def visit_ExpressionStmt(self, node: ExpressionStmt):
        self.analyze(node.expression)

    def visit_Comment(self, node: Comment):
        # 注释无需处理
        pass

    def visit_BinaryOp(self, node: BinaryOp) -> Type:
        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)
        op = node.operator

        arithmetic_ops = {'+', '-', '*', '/', '%'}
        comparison_ops = {'==', '!=', '<', '>', '<=', '>='}
        logical_ops = {'&&', '||'}

        if op in arithmetic_ops:
            if left_type.name in {'int', 'float'} and right_type.name in {'int', 'float'}:
                return Type('float') if 'float' in (left_type.name, right_type.name) else Type('int')
            else:
                raise SemanticError(f"Arithmetic operator '{op}' requires numeric operands.", node)
        elif op in comparison_ops:
            if left_type == right_type:
                return Type('bool')
            else:
                raise SemanticError(f"Comparison operator '{op}' requires operands of the same type.", node)
        elif op in logical_ops:
            if left_type.name == 'bool' and right_type.name == 'bool':
                return Type('bool')
            else:
                raise SemanticError(f"Logical operator '{op}' requires boolean operands.", node)
        else:
            raise SemanticError(f"Unknown binary operator '{op}'.", node)

    def visit_UnaryOp(self, node: UnaryOp) -> Type:
        operand_type = self.analyze(node.operand)
        op = node.operator

        if op == '!':
            if operand_type.name == 'bool':
                return Type('bool')
            else:
                raise SemanticError(f"Logical NOT operator '!' requires a boolean operand.", node)
        elif op == '-':
            if operand_type.name in {'int', 'float'}:
                return operand_type
            else:
                raise SemanticError(f"Unary minus operator '-' requires a numeric operand.", node)
        else:
            raise SemanticError(f"Unknown unary operator '{op}'.", node)

    def visit_Literal(self, node: Literal) -> Type:
        return self.resolve_type(node.type)

    def visit_Variable(self, node: Variable) -> Type:
        symbol = self.current_scope.lookup(node.name)
        if not symbol:
            raise SemanticError(f"Undefined variable '{node.name}'.", node)
        return symbol.data_type  # 返回 Type 对象

    def visit_FunctionCall(self, node: FunctionCall) -> Type:
        # 检查是否是库函数
        if node.name in self.library_functions:
            lib_func = self.library_functions[node.name]
            func_symbol = self.global_scope.lookup(node.name)
            
            # 如果是可变参数函数，不检查参数数量
            if not func_symbol.is_variadic:
                if len(node.arguments) != len(lib_func.params):
                    raise SemanticError(f"Function '{node.name}' expects {len(lib_func.params)} parameters, got {len(node.arguments)}.", node)
                
                # 检查参数类型
                for arg, param in zip(node.arguments, lib_func.params):
                    arg_type = self.analyze(arg)
                    param_type = self.resolve_type(param.type)
                    if param_type.name != 'any' and not self.type_compatible(param_type, arg_type):
                        raise SemanticError(f"Type mismatch in function '{node.name}' argument '{param.name}': expected '{param_type.name}', got '{arg_type.name}'.", node)
            
            # 返回函数返回类型
            return self.resolve_type(lib_func.return_type)
        
        func_symbol = self.current_scope.lookup(node.name)
        if not func_symbol:
            raise SemanticError(f"Undefined function '{node.name}'.", node)
        if not func_symbol.is_function:
            raise SemanticError(f"'{node.name}' is not a function.", node)
        if len(func_symbol.params) != len(node.arguments):
            raise SemanticError(f"Function '{node.name}' expects {len(func_symbol.params)} parameters, got {len(node.arguments)}.", node)
        # 检查参数类型
        for ((param_name, param_type), arg_expr) in zip(func_symbol.params, node.arguments):
            arg_type = self.analyze(arg_expr)
            if not self.type_compatible(param_type, arg_type):
                raise SemanticError(f"Type mismatch in function '{node.name}' argument '{param_name}': expected '{param_type.name}', got '{arg_type.name}'.", node)
        return func_symbol.data_type

    def visit_ListLiteral(self, node: ListLiteral) -> ListType:
        if not node.elements:
            raise SemanticError("List cannot be empty; element type cannot be inferred.", node)
        # 假设所有元素类型相同，取第一个元素的类型
        first_element_type = self.analyze(node.elements[0])
        for elem in node.elements[1:]:
            elem_type = self.analyze(elem)
            if not self.type_compatible(first_element_type, elem_type):
                raise SemanticError("All elements in the list must have the same type.", node)
        return ListType(element_type=first_element_type)

    def visit_TupleLiteral(self, node: TupleLiteral) -> TupleType:
        element_types = [self.analyze(elem) for elem in node.elements]
        return TupleType(element_types=element_types)

    def visit_IndexAccess(self, node: IndexAccess) -> Type:
        # 分析集合表达式，获取其类型
        collection_type = self.analyze(node.collection)

        # 检查集合类型是否为 list 或 tuple
        if isinstance(collection_type, ListType):
            collection_element_type = collection_type.element_type
        elif isinstance(collection_type, TupleType):
            # 元组的索引必须是常量表达式，这里简化处理
            # 假设索引为整数，并且在编译时能够确定具体类型
            if isinstance(node.index, Literal) and node.index.type == 'int':
                index = node.index.value
                if 0 <= index < len(collection_type.element_types):
                    collection_element_type = collection_type.element_types[index]
                else:
                    raise SemanticError(f"Tuple index {index} out of range.", node)
            else:
                # 无法确定具体索引，返回可能的元素类型（假设为 'any' 或引发错误）
                # 这里选择引发错误，要求索引为常量整数
                raise SemanticError("Tuple index must be a constant integer.", node)
        else:
            raise SemanticError("Indexing is only supported on 'list' and 'tuple' types.", node)

        # 分析索引表达式，确保其为 int 类型
        index_type = self.analyze(node.index)
        if not self.type_compatible(Type('int'), index_type):
            raise SemanticError(f"Index expression must be of type 'int', got '{index_type.name}'.", node)

        return collection_element_type

    def visit_ArrayAccess(self, node: ArrayAccess) -> Type:
        # 与 IndexAccess 类似，可以根据需要合并处理
        return self.visit_IndexAccess(node)

    def visit_IfStmt(self, node: IfStmt):
        # 分析条件
        condition_type = self.analyze(node.condition)
        if condition_type.name != 'bool':
            raise SemanticError(f"If statement condition must be 'bool', got '{condition_type.name}'.", node)
        # 分析 then_branch
        self.analyze(node.then_branch)
        # 分析 elif_branches
        for elif_branch in node.elif_branches:
            self.analyze(elif_branch)
        # 分析 else_branch
        if node.else_branch:
            self.analyze(node.else_branch)

    def visit_ElifBranch(self, node: ElifBranch):
        # 分析条件
        condition_type = self.analyze(node.condition)
        if condition_type.name != 'bool':
            raise SemanticError(f"Elif statement condition must be 'bool', got '{condition_type.name}'.", node)
        # 分析 body
        self.analyze(node.body)

    def visit_ForStmt(self, node: ForStmt):
        # 分析 initializer
        if node.initializer:
            self.analyze(node.initializer)
        # 分析 condition
        if node.condition:
            condition_type = self.analyze(node.condition)
            if condition_type.name != 'bool':
                raise SemanticError(f"For loop condition must be 'bool', got '{condition_type.name}'.", node)
        # 分析 update
        if node.update:
            self.analyze(node.update)
        # 分析 body
        self.analyze(node.body)

    def visit_BreakStmt(self, node: BreakStmt):
        # 可以在循环上下文中添加检查，暂时忽略
        pass

    def visit_ContinueStmt(self, node: ContinueStmt):
        # 可以在循环上下文中添加检查，暂时忽略
        pass

    def resolve_type(self, type_str: str) -> Type:
        """解析类型字符串，返回对应的 Type 对象"""
        if type_str.startswith('list<') and type_str.endswith('>'):
            # 解析 list 的元素类型
            inner_type_str = type_str[5:-1].strip()
            element_type = self.resolve_type(inner_type_str)
            return ListType(element_type=element_type)
        elif type_str.startswith('tuple<') and type_str.endswith('>'):
            # 解析 tuple 的元素类型列表
            inner_types_str = type_str[6:-1].strip()
            # 简单的分割，假设类型名中不含逗号
            type_names = [t.strip() for t in inner_types_str.split(',')]
            element_types = [self.resolve_type(t) for t in type_names]
            return TupleType(element_types=element_types)
        else:
            # 基本类型
            return Type(type_str)

    def type_compatible(self, expected: Type, actual: Type) -> bool:
        """检查类型是否兼容"""
        if expected == actual:
            return True
        # 自动将 int 转换为 float
        if isinstance(expected, Type) and isinstance(actual, Type):
            if expected.name == 'float' and actual.name == 'int':
                return True
        # 列表类型兼容性
        if isinstance(expected, ListType) and isinstance(actual, ListType):
            return self.type_compatible(expected.element_type, actual.element_type)
        # 元组类型兼容性
        if isinstance(expected, TupleType) and isinstance(actual, TupleType):
            if len(expected.element_types) != len(actual.element_types):
                return False
            return all(self.type_compatible(e, a) for e, a in zip(expected.element_types, actual.element_types))
        # 其他类型兼容规则
        return False

    def find_enclosing_function(self) -> Optional[Symbol]:
        """查找当前作用域中最近的函数符号"""
        scope = self.current_scope
        while scope:
            for symbol in scope.symbols.values():
                if symbol.is_function:
                    return symbol
            scope = scope.parent
        return None
