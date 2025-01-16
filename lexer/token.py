import re
from enum import Enum, auto

class TokenType(Enum):
    # 关键字
    KEYWORD = auto()
    # 标识符
    IDENTIFIER = auto()
    # 整数常量
    INTEGER_LITERAL = auto()
    # 浮点数常量
    FLOAT_LITERAL = auto()
    # 布尔常量
    BOOLEAN_LITERAL = auto()
    # 字符串字面量
    STRING_LITERAL = auto()
    # 运算符 将必要的操作符 集成在一起
    OPERATOR = auto()
    # 注释
    COMMENT = auto()
    # 错误
    ERROR = auto()
    # 结束标志
    EOF = auto()

# 自定义语言的关键字列表
CUSTOM_KEYWORDS = {
    'nil', 'bool', 'true', 'false', 'int', 'float', 'str', 'tuple',
    'list', 'fn', 'import', 'for', 'if', 'elif', 'else', 'continue',
    'break', 'return','class'
}

# 自定义语言的运算符列表（按长度降序排列以优先匹配多字符运算符）
CUSTOM_OPERATORS = [
    '+=', '-=', '*=', '/=', '==', '!=', '<=', '>=', '&&', '||',
    '++', '--', '->', '=>', '::', '+=', '-=', '*=', '/=',
    '+', '-', '*', '/', '%', '=', '<', '>', '!', '&', '|', '^',
    '~', '?', ':', ';', ',', '.', '(', ')', '{', '}', '[', ']', 
]

# 为了避免 regex 的优先级问题，按照长度降序排序
CUSTOM_OPERATORS.sort(key=lambda x: -len(x))

# 转义所有操作符
escaped_operators = [re.escape(op) for op in CUSTOM_OPERATORS]

# 构建操作符的正则表达式，使用 | 进行分隔
OPERATORS_REGEX = '|'.join(escaped_operators)

# 正则表达式模式
TOKEN_SPECIFICATION = [
    ('COMMENT',         r'//.*|/\*[\s\S]*?\*/'),  # 单行和多行注释
    ('STRING_LITERAL',  r'"(\\.|[^"\\])*"|\'(\\.|[^\'\\])*\''),
    ('FLOAT_LITERAL',   r'\b\d+\.\d*([eE][+-]?\d+)?\b|\b\d*\.\d+([eE][+-]?\d+)?\b'),
    ('INTEGER_LITERAL', r'\b\d+\b'),
    ('BOOLEAN_LITERAL', r'\b(true|false)\b'),
    ('IDENTIFIER',      r'\b[A-Za-z_][A-Za-z0-9_]*\b'),
    ('OPERATOR',        OPERATORS_REGEX),
    ('NEWLINE',         r'\n'),  # 行结束
    ('SKIP',            r'[ \t\r]+'),  # 跳过空白字符
    ('MISMATCH',        r'.'),  # 任何不匹配的字符
]

# 编译正则表达式
tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
try:
    get_token = re.compile(tok_regex).match
except re.error as e:
    print(f"正则表达式编译错误: {e}")
    exit(1)

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f'Token<{self.type.name}, {repr(self.value)}, Line:{self.line}, Column:{self.column}>'



