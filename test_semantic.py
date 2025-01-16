# main.py
from lexer import Lexer
from parser import Parser, ParserError
from semantic import SemanticAnalyzer, SemanticError
from ast_nodes import Program

def main():
    sample_code = open('code.me', 'r', encoding="utf-8").read()

    # 词法分析
    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()

    # 语法分析
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except ParserError as pe:
        print(pe)
        return

    # 语义分析
    analyzer = SemanticAnalyzer()
    try:
        analyzer.analyze(ast)
        print("语义分析成功，没有发现错误。")
    except SemanticError as se:
        print(se)

if __name__ == "__main__":
    main()
