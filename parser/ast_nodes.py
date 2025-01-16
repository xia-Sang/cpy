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
class UnaryOp(ASTNode):
    def __init__(self, operator: str, operand: "Expression", is_prefix: bool = False):
        self.operator = operator
        self.operand = operand
        self.is_prefix = is_prefix

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
