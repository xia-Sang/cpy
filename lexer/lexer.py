from .token import CUSTOM_KEYWORDS, Token,TokenType,get_token
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
    sample_code =open('code.me', 'r',encoding="utf-8").read()

    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)