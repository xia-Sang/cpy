from dataclasses import dataclass
from typing import List, Optional, Union

# 基础节点类
class ASTNode:
    def to_dict(self):
        """将 AST 节点转换为字典表示"""
        return {
            'type': self.__class__.__name__,
            'data': self.__dict__
        }

# 程序节点，包含多个声明
@dataclass
class Program(ASTNode):
    declarations: List[ASTNode]

# 导入语句
@dataclass
class ImportStatement(ASTNode):
    modules: List[str]

# 函数定义
@dataclass
class FunctionDecl(ASTNode):
    return_type: str
    name: str
    params: List['Parameter']
    body: 'CompoundStmt'

# 参数
@dataclass
class Parameter(ASTNode):
    type: str
    name: str

# 变量声明
@dataclass
class VarDecl(ASTNode):
    var_type: str
    name: str
    init_value: Optional['Expression'] = None

# 数组声明
@dataclass
class ArrayDecl(ASTNode):
    var_type: str
    name: str
    size: 'Expression'
    init_values: Optional[List['Expression']] = None

# 复合语句（块）
@dataclass
class CompoundStmt(ASTNode):
    statements: List[ASTNode]

# 返回语句
@dataclass
class ReturnStmt(ASTNode):
    expr: 'Expression'

# 表达式语句
@dataclass
class ExpressionStmt(ASTNode):
    expression: 'Expression'

# 注释
@dataclass
class Comment(ASTNode):
    value: str

# 二元表达式
@dataclass
class BinaryOp(ASTNode):
    left: 'Expression'
    operator: str
    right: 'Expression'

# 一元表达式
@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: 'Expression'
    is_prefix: bool = True  # True 表示前缀，False 表示后缀

# 字面量
@dataclass
class Literal(ASTNode):
    type: str
    value: Union[int, float, bool, str, None]

# 变量引用
@dataclass
class Variable(ASTNode):
    name: str

# 函数调用
@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List['Expression']

# 赋值语句
@dataclass
class Assignment(ASTNode):
    target: 'Expression'
    operator: str  # '=', '+=', '-=', etc.
    value: 'Expression'

# 条件语句（if-elif-else）
@dataclass
class IfStmt(ASTNode):
    condition: 'Expression'
    then_branch: 'CompoundStmt'
    elif_branches: List['ElifBranch']
    else_branch: Optional['CompoundStmt'] = None

@dataclass
class ElifBranch(ASTNode):
    condition: 'Expression'
    body: 'CompoundStmt'

# 循环语句（for）
@dataclass
class ForStmt(ASTNode):
    initializer: Optional[ASTNode]
    condition: Optional['Expression']
    update: Optional['Expression']
    body: 'CompoundStmt'

# 循环控制语句
@dataclass
class BreakStmt(ASTNode):
    pass

@dataclass
class ContinueStmt(ASTNode):
    pass

# 数组访问
@dataclass
class ArrayAccess(ASTNode):
    array: 'Expression'
    index: 'Expression'

# 表达式基类
class Expression(ASTNode):
    pass

# 元组字面量
@dataclass
class TupleLiteral(Expression):
    elements: List['Expression']

# 列表字面量
@dataclass
class ListLiteral(Expression):
    elements: List['Expression']


@dataclass
class ClassDecl(ASTNode):
    name: str
    base_class: Optional[str]  # 基类名称，支持单继承
    members: List[ASTNode]      # 类的成员变量和方法


@dataclass
class MemberVarDecl(ASTNode):
    var_type: str
    name: str
    init_value: Optional['Expression'] = None
    is_public: bool = False  # 根据命名约定决定


@dataclass
class MemberFunctionDecl(ASTNode):
    return_type: str
    name: str
    params: List['Parameter']
    body: 'CompoundStmt'
    is_public: bool = False  # 根据命名约定决定
# 元素访问表达式
@dataclass
class IndexAccess(Expression):
    collection: Expression  # 被访问的集合（tuple 或 list）
    index: Expression       # 索引表达式
    
    
def print_ast(node: ASTNode, indent: int = 0):
    """递归打印AST节点，使用缩进表示层级"""
    prefix = '  ' * indent
    if isinstance(node, Program):
        print(f"{prefix}Program:")
        for decl in node.declarations:
            print_ast(decl, indent + 1)
    elif isinstance(node, ImportStatement):
        print(f"{prefix}ImportStatement:")
        print(f"{prefix}  modules: {node.modules}")
    elif isinstance(node, ClassDecl):
        base = node.base_class if node.base_class else "None"
        print(f"{prefix}ClassDecl:")
        print(f"{prefix}  name: {node.name}")
        print(f"{prefix}  base_class: {base}")
        print(f"{prefix}  members:")
        for member in node.members:
            print_ast(member, indent + 2)
    elif isinstance(node, MemberVarDecl):
        access = 'public' if node.is_public else 'private'
        print(f"{prefix}MemberVarDecl (access: {access}):")
        print(f"{prefix}  var_type: {node.var_type}")
        print(f"{prefix}  name: {node.name}")
        if node.init_value:
            print(f"{prefix}  init_value:")
            print_ast(node.init_value, indent + 2)
    elif isinstance(node, MemberFunctionDecl):
        access = 'public' if node.is_public else 'private'
        print(f"{prefix}MemberFunctionDecl (access: {access}):")
        print(f"{prefix}  return_type: {node.return_type}")
        print(f"{prefix}  name: {node.name}")
        print(f"{prefix}  params:")
        for param in node.params:
            print_ast(param, indent + 2)
        print(f"{prefix}  body:")
        print_ast(node.body, indent + 2)
    elif isinstance(node, FunctionDecl):
        print(f"{prefix}FunctionDecl:")
        print(f"{prefix}  return_type: {node.return_type}")
        print(f"{prefix}  name: {node.name}")
        print(f"{prefix}  params:")
        for param in node.params:
            print_ast(param, indent + 2)
        print(f"{prefix}  body:")
        print_ast(node.body, indent + 2)
    elif isinstance(node, Parameter):
        print(f"{prefix}Parameter:")
        print(f"{prefix}  type: {node.type}")
        print(f"{prefix}  name: {node.name}")
    elif isinstance(node, CompoundStmt):
        print(f"{prefix}CompoundStmt:")
        for stmt in node.statements:
            print_ast(stmt, indent + 1)
    elif isinstance(node, VarDecl):
        print(f"{prefix}VarDecl:")
        print(f"{prefix}  var_type: {node.var_type}")
        print(f"{prefix}  name: {node.name}")
        if node.init_value:
            print(f"{prefix}  init_value:")
            print_ast(node.init_value, indent + 2)
    elif isinstance(node, ArrayDecl):
        print(f"{prefix}ArrayDecl:")
        print(f"{prefix}  var_type: {node.var_type}")
        print(f"{prefix}  name: {node.name}")
        print(f"{prefix}  size:")
        print_ast(node.size, indent + 2)
        if node.init_values:
            print(f"{prefix}  init_values:")
            for val in node.init_values:
                print_ast(val, indent + 2)
    elif isinstance(node, ReturnStmt):
        print(f"{prefix}ReturnStmt:")
        print(f"{prefix}  expr:")
        print_ast(node.expr, indent + 2)
    elif isinstance(node, ExpressionStmt):
        print(f"{prefix}ExpressionStmt:")
        print_ast(node.expression, indent + 1)
    elif isinstance(node, Comment):
        print(f"{prefix}Comment:")
        print(f"{prefix}  value: {node.value}")
    elif isinstance(node, BinaryOp):
        print(f"{prefix}BinaryOp:")
        print(f"{prefix}  left:")
        print_ast(node.left, indent + 2)
        print(f"{prefix}  operator: {node.operator}")
        print(f"{prefix}  right:")
        print_ast(node.right, indent + 2)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnaryOp:")
        print(f"{prefix}  operator: {node.operator}")
        print(f"{prefix}  operand:")
        print_ast(node.operand, indent + 2)
        print(f"{prefix}  is_prefix: {node.is_prefix}")
    elif isinstance(node, Literal):
        print(f"{prefix}Literal:")
        print(f"{prefix}  type: {node.type}")
        print(f"{prefix}  value: {node.value}")
    elif isinstance(node, Variable):
        print(f"{prefix}Variable:")
        print(f"{prefix}  name: {node.name}")
    elif isinstance(node, FunctionCall):
        print(f"{prefix}FunctionCall:")
        print(f"{prefix}  name: {node.name}")
        print(f"{prefix}  arguments:")
        for arg in node.arguments:
            print_ast(arg, indent + 2)
    elif isinstance(node, Assignment):
        print(f"{prefix}Assignment:")
        print(f"{prefix}  target:")
        print_ast(node.target, indent + 2)
        print(f"{prefix}  operator: {node.operator}")
        print(f"{prefix}  value:")
        print_ast(node.value, indent + 2)
    elif isinstance(node, IfStmt):
        print(f"{prefix}IfStmt:")
        print(f"{prefix}  condition:")
        print_ast(node.condition, indent + 2)
        print(f"{prefix}  then_branch:")
        print_ast(node.then_branch, indent + 2)
        if node.elif_branches:
            print(f"{prefix}  elif_branches:")
            for elif_branch in node.elif_branches:
                print_ast(elif_branch, indent + 2)
        if node.else_branch:
            print(f"{prefix}  else_branch:")
            print_ast(node.else_branch, indent + 2)
    elif isinstance(node, ElifBranch):
        print(f"{prefix}ElifBranch:")
        print(f"{prefix}  condition:")
        print_ast(node.condition, indent + 2)
        print(f"{prefix}  body:")
        print_ast(node.body, indent + 2)
    elif isinstance(node, ForStmt):
        print(f"{prefix}ForStmt:")
        if node.initializer:
            print(f"{prefix}  initializer:")
            print_ast(node.initializer, indent + 2)
        if node.condition:
            print(f"{prefix}  condition:")
            print_ast(node.condition, indent + 2)
        if node.update:
            print(f"{prefix}  update:")
            print_ast(node.update, indent + 2)
        print(f"{prefix}  body:")
        print_ast(node.body, indent + 2)
    elif isinstance(node, BreakStmt):
        print(f"{prefix}BreakStmt")
    elif isinstance(node, ContinueStmt):
        print(f"{prefix}ContinueStmt")
    elif isinstance(node, ArrayAccess):
        print(f"{prefix}ArrayAccess:")
        print(f"{prefix}  array:")
        print_ast(node.array, indent + 2)
        print(f"{prefix}  index:")
        print_ast(node.index, indent + 2)
    elif isinstance(node, TupleLiteral):
        print(f"{prefix}TupleLiteral:")
        print(f"{prefix}  elements:")
        for elem in node.elements:
            print_ast(elem, indent + 2)
    elif isinstance(node, ListLiteral):
        print(f"{prefix}ListLiteral:")
        print(f"{prefix}  elements:")
        for elem in node.elements:
            print_ast(elem, indent + 2)
    elif isinstance(node, IndexAccess):
        print(f"{prefix}IndexAccess:")
        print(f"{prefix}  collection:")
        print_ast(node.collection, indent + 2)
        print(f"{prefix}  index:")
        print_ast(node.index, indent + 2)
    else:
        print(f"{prefix}{type(node).__name__} not handled.")

class LibraryCall(ASTNode):
    """表示库函数调用"""
    def __init__(self, name: str, arguments: List[ASTNode]):
        self.name = name
        self.arguments = arguments
    def to_dict(self):
        return {
            'type': self.__class__.__name__,
            'data': {'name': self.name, 'arguments': [arg.to_dict() for arg in self.arguments]}
        }
