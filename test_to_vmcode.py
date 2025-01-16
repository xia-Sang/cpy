# main.py

from code_generator import CodeGenerator
from lexer import Lexer
from parser import Parser, ParserError
from semantic import SemanticAnalyzer, SemanticError
from simple_vm import run_tac_program
from ast_nodes import print_ast
def main():
    sample_code = open('code.me', 'r', encoding="utf-8").read()

    # 1. 词法分析
    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()

    # 2. 语法分析
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except ParserError as pe:
        print(pe)
        return
    print_ast(ast)
    # 3. 语义分析
    analyzer = SemanticAnalyzer()
    try:
        analyzer.analyze(ast)
        print("语义分析成功，没有发现错误。")

        # 4. 代码生成(三地址码)
        generator = CodeGenerator()
        intermediate_code = generator.generate(ast)

        # 打印中间代码(TAC)
        print("\n=== 三地址码 (TAC) ===")
        print(intermediate_code)
        ans = run_tac_program(intermediate_code, debug=False)
        print(ans)


    except SemanticError as se:
        print(se)


if __name__ == "__main__":
    main()
