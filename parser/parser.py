from typing import List, Optional, Union
from .ast_nodes import *
from lexer.token import Token, TokenType

class ParserError(Exception):
    def __init__(self, message, token):
        super().__init__(
            f"Parser error: {message} at line {token.line}, column {token.column}"
        )


class Parser:
    def __init__(self, tokens: List["Token"]):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]

    def error(self, message):
        raise ParserError(message, self.current_token)

    def optional_eat(self, token_type: TokenType, value: Optional[str] = None):
        """可选地消费一个指定类型和值的标记。如果匹配，则前进，否则不做任何操作。"""
        if self.current_token.type == token_type and (
            value is None or self.current_token.value == value
        ):
            self.eat(token_type, value)

    def eat(self, token_type: TokenType, value: Optional[str] = None):
        if self.current_token.type == token_type and (
            value is None or self.current_token.value == value
        ):
            self.current_token_index += 1
            if self.current_token_index < len(self.tokens):
                self.current_token = self.tokens[self.current_token_index]
            else:
                # 如果已到达 tokens 列表末尾，设置为 EOF
                self.current_token = Token(
                    TokenType.EOF,
                    "",
                    self.current_token.line,
                    self.current_token.column + 1,
                )
        else:
            expected = f"{token_type.name}" + (
                f" with value '{value}'" if value else ""
            )
            actual = f"{self.current_token.type.name} ('{self.current_token.value}')"
            self.error(f"Expected {expected}, got {actual}")

    def parse(self) -> Program:
        return self.program()

    def program(self) -> Program:
        declarations = []
        while self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.COMMENT:
                declarations.append(self.comment())
            elif self.current_token.type == TokenType.KEYWORD:
                if self.current_token.value == "import":
                    declarations.append(self.import_statement())
                elif self.current_token.value == "fn":
                    declarations.append(self.function_decl())
                elif self.current_token.value == "class":
                    declarations.append(self.class_decl())
                else:
                    self.error(
                        f"Unexpected keyword '{self.current_token.value}' at top level"
                    )
            else:
                self.error("Invalid statement at top level")
        return Program(declarations)
    def class_decl(self) -> ClassDecl:
        self.eat(TokenType.KEYWORD, 'class')
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected class name after 'class'")
        class_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # 检查是否有继承关系
        base_class = None
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '[':
            self.eat(TokenType.OPERATOR, '[')
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected base class name inside '[]'")
            base_class = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.OPERATOR, ']')
        
        # 解析类体
        members = self.class_body()
        return ClassDecl(class_name, base_class, members)
    def class_decl(self) -> ClassDecl:
        self.eat(TokenType.KEYWORD, 'class')
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected class name after 'class'")
        class_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # 检查是否有继承关系
        base_class = None
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '[':
            self.eat(TokenType.OPERATOR, '[')
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected base class name inside '[]'")
            base_class = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.OPERATOR, ']')
        
        # 解析类体
        members = self.class_body()
        return ClassDecl(class_name, base_class, members)
    def class_body(self) -> List[ASTNode]:
        self.eat(TokenType.OPERATOR, '{')
        members = []
        while not (self.current_token.type == TokenType.OPERATOR and self.current_token.value == '}'):
            if self.current_token.type == TokenType.COMMENT:
                members.append(self.comment())
            elif self.current_token.type == TokenType.KEYWORD:
                if self.current_token.value == 'fn':
                    members.append(self.member_function_decl())
                elif self.current_token.value in ['nil', 'bool', 'int', 'float', 'str', 'tuple', 'list']:
                    members.append(self.member_var_decl())
                else:
                    self.error(f"Unexpected keyword '{self.current_token.value}' in class body")
            else:
                self.error("Invalid member in class body")
            # 可选地消费分号
            self.optional_eat(TokenType.OPERATOR, ';')
        self.eat(TokenType.OPERATOR, '}')
        return members
    def member_var_decl(self) -> MemberVarDecl:
        var_type = self.current_token.value
        self.eat(TokenType.KEYWORD)
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected member variable name after type")
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        init_value = None
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '=':
            self.eat(TokenType.OPERATOR, '=')
            init_value = self.expression()
        # 判断访问控制
        is_public = var_name[0].isupper()
        return MemberVarDecl(var_type, var_name, init_value, is_public)
    def member_function_decl(self) -> MemberFunctionDecl:
        self.eat(TokenType.KEYWORD, 'fn')
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected method name after 'fn'")
        method_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.OPERATOR, '(')
        params = self.parameter_list()
        self.eat(TokenType.OPERATOR, ')')
        self.eat(TokenType.OPERATOR, '->')
        if self.current_token.type not in [TokenType.KEYWORD, TokenType.IDENTIFIER]:
            self.error("Expected return type after '->'")
        return_type = self.current_token.value
        self.eat(self.current_token.type)  # Eat return type
        body = self.compound_statement()
        # 判断访问控制
        is_public = method_name[0].isupper()
        return MemberFunctionDecl(return_type, method_name, params, body, is_public)

    def comment(self) -> Comment:
        value = self.current_token.value
        self.eat(TokenType.COMMENT)
        return Comment(value)

    def import_statement(self) -> ImportStatement:
        self.eat(TokenType.KEYWORD, 'import')
        modules = []

        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '(':
            # 处理多个导入
            self.eat(TokenType.OPERATOR, '(')
            while self.current_token.type == TokenType.STRING_LITERAL:
                module = self.current_token.value.strip('"').strip("'")
                modules.append(module)
                self.eat(TokenType.STRING_LITERAL)
            self.eat(TokenType.OPERATOR, ')')
        elif self.current_token.type == TokenType.STRING_LITERAL:
            # 处理单个导入
            module = self.current_token.value.strip('"').strip("'")
            modules.append(module)
            self.eat(TokenType.STRING_LITERAL)
        else:
            self.error("Expected string literal or '(' after 'import'")

        # 可选地消费分号
        self.optional_eat(TokenType.OPERATOR, ';')
        return ImportStatement(modules)

    def function_decl(self) -> FunctionDecl:
        self.eat(TokenType.KEYWORD, "fn")
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected function name after 'fn'")
        func_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.OPERATOR, "(")
        params = self.parameter_list()
        self.eat(TokenType.OPERATOR, ")")
        self.eat(TokenType.OPERATOR, "->")
        
        # 解析返回类型，包括元组类型
        if self.current_token.type not in [TokenType.KEYWORD, TokenType.IDENTIFIER]:
            self.error("Expected return type after '->'")
        return_type = self.parse_type()  # 使用 parse_type 而不是直接获取 value
        
        body = self.compound_statement()
        return FunctionDecl(return_type, func_name, params, body)

    def parameter_list(self) -> List[Parameter]:
        params = []
        if (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == ")"
        ):
            return params
        while True:
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error("Expected parameter name")
            param_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.OPERATOR, ":")
            if self.current_token.type not in [TokenType.KEYWORD, TokenType.IDENTIFIER]:
                self.error("Expected parameter type after ':'")
            param_type = self.current_token.value
            self.eat(self.current_token.type)  # Eat type
            params.append(Parameter(param_type, param_name))
            if (
                self.current_token.type == TokenType.OPERATOR
                and self.current_token.value == ","
            ):
                self.eat(TokenType.OPERATOR, ",")
            else:
                break
        return params

    def compound_statement(self) -> CompoundStmt:
        self.eat(TokenType.OPERATOR, "{")
        statements = []
        while not (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == "}"
        ):
            if self.current_token.type == TokenType.COMMENT:
                statements.append(self.comment())
            elif self.current_token.type == TokenType.KEYWORD:
                if self.current_token.value in [
                    "nil",
                    "bool",
                    "int",
                    "float",
                    "str",
                    "tuple",
                    "list",
                ]:
                    statements.append(self.var_decl())
                elif self.current_token.value == "return":
                    statements.append(self.return_stmt())
                elif self.current_token.value == "if":
                    statements.append(self.if_stmt())
                elif self.current_token.value == "for":
                    statements.append(self.for_stmt())
                elif self.current_token.value == "break":
                    statements.append(self.break_stmt())
                elif self.current_token.value == "continue":
                    statements.append(self.continue_stmt())
                else:
                    self.error(
                        f"Unexpected keyword '{self.current_token.value}' in function body"
                    )
            elif self.current_token.type == TokenType.IDENTIFIER:
                # 可能是赋值语句或函数调用
                statements.append(self.statement())
            elif (
                self.current_token.type == TokenType.OPERATOR
                and self.current_token.value in ["++", "--"]
            ):
                # 前缀自增/自减
                statements.append(self.increment_statement())
            else:
                self.error("Invalid statement in compound block")
        self.eat(TokenType.OPERATOR, "}")
        return CompoundStmt(statements)

    def var_decl(self) -> Union[VarDecl, ArrayDecl]:
        """解析变量声明，如 'int x;' 或 'list<int> numbers = [1, 2, 3];'"""
        var_type = self.parse_type()
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected variable name after type")
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)

        init_value = None
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '=':
            self.eat(TokenType.OPERATOR, '=')
            init_value = self.expression()

        self.optional_eat(TokenType.OPERATOR, ';')
        return VarDecl(var_type=var_type, name=var_name, init_value=init_value)
    def array_initializer(self) -> List["Expression"]:
        # 数组初始化使用方括号 [1, 2, 3]
        self.eat(TokenType.OPERATOR, "[")
        values = []
        if (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == "]"
        ):
            self.eat(TokenType.OPERATOR, "]")
            return values
        values.append(self.expression())
        while (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == ","
        ):
            self.eat(TokenType.OPERATOR, ",")
            values.append(self.expression())
        self.eat(TokenType.OPERATOR, "]")
        return values

    def return_stmt(self) -> ReturnStmt:
        self.eat(TokenType.KEYWORD, "return")
        expr = self.expression()
        self.optional_eat(TokenType.OPERATOR, ";")
        return ReturnStmt(expr)

    def if_stmt(self) -> IfStmt:
        self.eat(TokenType.KEYWORD, "if")
        self.eat(TokenType.OPERATOR, "(")
        condition = self.expression()
        self.eat(TokenType.OPERATOR, ")")
        then_branch = self.compound_statement()
        elif_branches = []
        else_branch = None
        while (
            self.current_token.type == TokenType.KEYWORD
            and self.current_token.value == "elif"
        ):
            self.eat(TokenType.KEYWORD, "elif")
            self.eat(TokenType.OPERATOR, "(")
            elif_condition = self.expression()
            self.eat(TokenType.OPERATOR, ")")
            elif_body = self.compound_statement()
            elif_branches.append(ElifBranch(elif_condition, elif_body))
        if (
            self.current_token.type == TokenType.KEYWORD
            and self.current_token.value == "else"
        ):
            self.eat(TokenType.KEYWORD, "else")
            else_branch = self.compound_statement()
        return IfStmt(condition, then_branch, elif_branches, else_branch)

    def for_stmt(self) -> ForStmt:
        self.eat(TokenType.KEYWORD, "for")
        self.eat(TokenType.OPERATOR, "(")

        # 初始化部分
        initializer = None
        if not (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == ";"
        ):
            if (
                self.current_token.type == TokenType.KEYWORD
                and self.current_token.value
                in ["nil", "bool", "int", "float", "str", "tuple", "list"]
            ):
                initializer = self.var_decl()
            else:
                initializer = self.assignment()
        else:
            self.eat(TokenType.OPERATOR, ";")

        # 条件部分
        condition = None
        if not (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == ";"
        ):
            condition = self.expression()
        self.eat(TokenType.OPERATOR, ";")

        # 更新部分
        update = None
        if not (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == ")"
        ):
            update = self.parse_update_expression()
        self.eat(TokenType.OPERATOR, ")")

        body = self.compound_statement()
        return ForStmt(initializer, condition, update, body)
    def parse_type(self) -> str:
        """解析类型，包括泛型类型如 list<int>, tuple<int, str, float>"""
        if self.current_token.type != TokenType.KEYWORD and self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected type name")

        base_type = self.current_token.value
        self.eat(self.current_token.type)  # 消费基本类型名

        # 处理泛型类型
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '<':
            self.eat(TokenType.OPERATOR, '<')
            type_params = []
            
            # 解析第一个类型参数
            type_params.append(self.parse_type())
            
            # 解析剩余的类型参数
            while self.current_token.type == TokenType.OPERATOR and self.current_token.value == ',':
                self.eat(TokenType.OPERATOR, ',')
                type_params.append(self.parse_type())
                
            self.eat(TokenType.OPERATOR, '>')
            
            # 构建完整的类型字符串
            if base_type == 'tuple':
                # 元组类型需要保留所有类型参数
                return f"tuple<{', '.join(type_params)}>"
            else:
                # 其他泛型类型（如list）只使用第一个类型参数
                return f"{base_type}<{type_params[0]}>"
        
        return base_type
    def parse_update_expression(self) -> Union[Assignment, UnaryOp, Expression]:
        """Parse update expression which can be assignment, prefix/postfix increment/decrement, or other expressions"""
        expr = self.expression()

        # Handle postfix increment/decrement
        if (
            isinstance(expr, Variable)
            and self.current_token.type == TokenType.OPERATOR
            and self.current_token.value in ["++", "--"]
        ):
            operator = self.current_token.value
            self.eat(TokenType.OPERATOR, operator)
            return UnaryOp(operator, expr, is_prefix=False)

        # Handle compound assignment operators
        elif (
            isinstance(expr, Variable)
            and self.current_token.type == TokenType.OPERATOR
            and self.current_token.value in ["+=", "-=", "*=", "/="]
        ):
            operator = self.current_token.value
            self.eat(TokenType.OPERATOR, operator)
            value = self.expression()
            return Assignment(expr, operator, value)

        # Handle prefix increment/decrement
        elif (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value in ["++", "--"]
        ):
            operator = self.current_token.value
            self.eat(TokenType.OPERATOR, operator)
            if isinstance(expr, Variable) or isinstance(expr, ArrayAccess):
                return UnaryOp(operator, expr, is_prefix=True)
            else:
                self.error("Invalid operand for prefix increment/decrement")

        # Handle simple assignment
        elif (
            isinstance(expr, Variable)
            and self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == "="
        ):
            self.eat(TokenType.OPERATOR, "=")
            value = self.expression()
            return Assignment(expr, "=", value)

        else:
            return expr

    def break_stmt(self) -> BreakStmt:
        self.eat(TokenType.KEYWORD, "break")
        self.optional_eat(TokenType.OPERATOR, ";")
        return BreakStmt()

    def continue_stmt(self) -> ContinueStmt:
        self.eat(TokenType.KEYWORD, "continue")
        self.optional_eat(TokenType.OPERATOR, ";")
        return ContinueStmt()

 
    def statement(self) -> ASTNode:
        if self.current_token.type == TokenType.KEYWORD:
            if self.current_token.value == 'return':
                return self.return_stmt()
            elif self.current_token.value == 'if':
                return self.if_stmt()
            elif self.current_token.value == 'for':
                return self.for_stmt()
            elif self.current_token.value in ['break', 'continue']:
                return self.control_stmt()
            elif self.current_token.value in ['nil', 'bool', 'int', 'float', 'str', 'tuple', 'list']:
                return self.var_decl()
            else:
                self.error(f"Unexpected keyword '{self.current_token.value}' in statement")
        else:
            # 尝试解析表达式语句（如赋值或函数调用）
            expr = self.expression()
            # 期望表达式作为语句后跟分号
            self.optional_eat(TokenType.OPERATOR, ';')
            return ExpressionStmt(expr)
    def assignment(self) -> Assignment:
        expr = self.logical_or()
        if isinstance(expr, Variable)  or isinstance(expr, IndexAccess):
            if self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['=', '+=', '-=', '*=', '/=']:
                operator = self.current_token.value
                self.eat(TokenType.OPERATOR, operator)
                value = self.assignment()  # 允许链式赋值
                return Assignment(expr, operator, value)
        return expr
    def increment_statement(self) -> UnaryOp:
        """解析前缀自增/自减语句"""
        operator = self.current_token.value
        self.eat(TokenType.OPERATOR)
        operand = self.variable()
        return UnaryOp(operator, operand, is_prefix=True)

    def expression(self) -> "Expression":
        return self.assignment()

    def logical_or(self) -> "Expression":
        node = self.logical_and()
        while (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == "||"
        ):
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            right = self.logical_and()
            node = BinaryOp(node, op, right)
        return node

    def logical_and(self) -> "Expression":
        node = self.equality()
        while (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value == "&&"
        ):
            op = self.current_token.value
            self.eat(TokenType.OPERATOR,op)
            right = self.equality()
            node = BinaryOp(node, op, right)
        return node

    def equality(self) -> "Expression":
        node = self.relational()
        while (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value in ["==", "!="]
        ):
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            right = self.relational()
            node = BinaryOp(node, op, right)
        return node

    def relational(self) -> "Expression":
        node = self.additive()
        while (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value in ["<", ">", "<=", ">="]
        ):
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            right = self.additive()
            node = BinaryOp(node, op, right)
        return node
    def comparison(self) -> Expression:
        """解析比较表达式"""
        expr = self.addition()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['<', '>', '<=', '>=']:
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            right = self.addition()
            expr = BinaryOp(left=expr, operator=op, right=right)
        return expr
    def addition(self) -> Expression:
        """解析加法和减法表达式"""
        expr = self.multiplication()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['+', '-']:
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            right = self.multiplication()
            expr = BinaryOp(left=expr, operator=op, right=right)
        return expr

    def multiplication(self) -> Expression:
        """解析乘法和除法表达式"""
        expr = self.unary()
        while self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['*', '/', '%']:
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            right = self.unary()
            expr = BinaryOp(left=expr, operator=op, right=right)
        return expr

    def additive(self) -> "Expression":
        node = self.multiplicative()
        while (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value in ["+", "-"]
        ):
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            right = self.multiplicative()
            node = BinaryOp(node, op, right)
        return node

    def multiplicative(self) -> "Expression":
        node = self.unary()
        while (
            self.current_token.type == TokenType.OPERATOR
            and self.current_token.value in ["*", "/", "%"]
        ):
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            right = self.unary()
            node = BinaryOp(node, op, right)
        return node

    def unary(self) -> Expression:
        """解析一元表达式"""
        if self.current_token.type == TokenType.OPERATOR and self.current_token.value in ['!', '-']:
            op = self.current_token.value
            self.eat(TokenType.OPERATOR, op)
            operand = self.unary()
            return UnaryOp(operator=op, operand=operand)
        return self.primary()
    def primary(self) -> Expression:
        token = self.current_token
        
        """解析基本表达式，包括变量、函数调用、字面量、列表和元组"""
        if self.current_token.type == TokenType.IDENTIFIER:
            return self.variable_or_function_call()
        elif token.type == TokenType.INTEGER_LITERAL:
            self.eat(TokenType.INTEGER_LITERAL)
            return Literal("int", int(token.value))
        elif token.type == TokenType.FLOAT_LITERAL:
            self.eat(TokenType.FLOAT_LITERAL)
            return Literal("float", float(token.value))
        elif token.type == TokenType.BOOLEAN_LITERAL:
            self.eat(TokenType.BOOLEAN_LITERAL)
            return Literal("bool", token.value == "true")
        elif token.type == TokenType.STRING_LITERAL:
            self.eat(TokenType.STRING_LITERAL)
            return Literal("str", token.value.strip('"').strip("'"))
        elif token.type == TokenType.IDENTIFIER:
            return self.variable_or_function_call()
        elif self.current_token.type == TokenType.OPERATOR and self.current_token.value == '(':
            # 可能是元组或括号表达式
            self.eat(TokenType.OPERATOR, '(')
            elements = []
            if not (self.current_token.type == TokenType.OPERATOR and self.current_token.value == ')'):
                elements.append(self.expression())
                while self.current_token.type == TokenType.OPERATOR and self.current_token.value == ',':
                    self.eat(TokenType.OPERATOR, ',')
                    elements.append(self.expression())
            self.eat(TokenType.OPERATOR, ')')
            if len(elements) == 1:
                # 单个元素，可能是括号表达式
                return elements[0]
            else:
                # 多个元素，元组字面量
                return TupleLiteral(elements=elements)
        elif self.current_token.type == TokenType.OPERATOR and self.current_token.value == '[':
            # 列表字面量
            self.eat(TokenType.OPERATOR, '[')
            elements = []
            if not (self.current_token.type == TokenType.OPERATOR and self.current_token.value == ']'):
                elements.append(self.expression())
                while self.current_token.type == TokenType.OPERATOR and self.current_token.value == ',':
                    self.eat(TokenType.OPERATOR, ',')
                    elements.append(self.expression())
            self.eat(TokenType.OPERATOR, ']')
            return ListLiteral(elements=elements)
        else:
            self.error("Unexpected token in primary expression")
   
    def variable_or_function_call(self) -> Expression:
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        expr = Variable(name=var_name)
        while True:
            if self.current_token.type == TokenType.OPERATOR and self.current_token.value == '(':
                expr = self.function_call(expr)
            elif self.current_token.type == TokenType.OPERATOR and self.current_token.value == '[':
                expr = self.index_access(expr)
            else:
                break
        return expr
   
    def function_call(self, func_expr: Expression) -> FunctionCall:
        if not isinstance(func_expr, Variable):
            self.error("Only simple function names are supported for function calls")
        func_name = func_expr.name
        self.eat(TokenType.OPERATOR, '(')
        args = []
        if not (self.current_token.type == TokenType.OPERATOR and self.current_token.value == ')'):
            args.append(self.expression())
            while self.current_token.type == TokenType.OPERATOR and self.current_token.value == ',':
                self.eat(TokenType.OPERATOR, ',')
                args.append(self.expression())
        self.eat(TokenType.OPERATOR, ')')
        return FunctionCall(name=func_name, arguments=args)

    def index_access(self, collection_expr: Expression) -> IndexAccess:
        self.eat(TokenType.OPERATOR, '[')
        index_expr = self.expression()
        self.eat(TokenType.OPERATOR, ']')
        return IndexAccess(collection=collection_expr, index=index_expr)