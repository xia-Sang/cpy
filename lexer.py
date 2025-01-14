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
    # 运算符
    OPERATOR = auto()
    # 分隔符
    SEPARATOR = auto()
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

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(code)
    
    def tokenize(self):
        tokens = []
        mo = get_token(self.code)
        while mo is not None:
            kind = mo.lastgroup
            value = mo.group(kind)
            if kind == 'NEWLINE':
                self.line += 1
                self.column = 1
            elif kind == 'SKIP':
                pass
            elif kind == 'COMMENT':
                tokens.append(Token(TokenType.COMMENT, value, self.line, self.column))
            elif kind == 'IDENTIFIER':
                if value in CUSTOM_KEYWORDS:
                    if value in {'true', 'false'}:
                        tokens.append(Token(TokenType.BOOLEAN_LITERAL, value, self.line, self.column))
                    else:
                        tokens.append(Token(TokenType.KEYWORD, value, self.line, self.column))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, value, self.line, self.column))
            elif kind == 'BOOLEAN_LITERAL':
                tokens.append(Token(TokenType.BOOLEAN_LITERAL, value, self.line, self.column))
            elif kind == 'INTEGER_LITERAL':
                tokens.append(Token(TokenType.INTEGER_LITERAL, value, self.line, self.column))
            elif kind == 'FLOAT_LITERAL':
                tokens.append(Token(TokenType.FLOAT_LITERAL, value, self.line, self.column))
            elif kind == 'STRING_LITERAL':
                tokens.append(Token(TokenType.STRING_LITERAL, value, self.line, self.column))
            elif kind == 'OPERATOR':
                tokens.append(Token(TokenType.OPERATOR, value, self.line, self.column))
            elif kind == 'MISMATCH':
                tokens.append(Token(TokenType.ERROR, value, self.line, self.column))
            self.pos = mo.end()
            self.column += mo.end() - mo.start()
            mo = get_token(self.code, self.pos)
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens

# 示例代码
if __name__ == "__main__":
    sample_code =open('code.cpy', 'r',encoding="utf-8").read()

    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)

KEYWORDS = {
    # ... 现有关键字 ...
    'print': 'PRINT',
    'input': 'INPUT',
}
