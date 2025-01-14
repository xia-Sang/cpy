from code_generator import CodeGenerator
from lexer import Lexer, TokenType  # 假设您的词法分析器在 lexer.py 中
from parser import Parser, ParserError  # 假设您将解析器代码保存为 parser.py
from ast_nodes import *  # 假设 AST 节点类在 ast_nodes.py 中
from simple_vm import run_tac_program

from ast_nodes import *




if __name__ == "__main__":
    try:
        with open("code.cpy", "r", encoding="utf-8") as f:
            sample_code = f.read()
    except FileNotFoundError:
        print("错误: 未找到 'code.pyc' 文件。请确保文件存在于当前目录。")
        exit(1)

    # 词法分析
    lexer = Lexer(sample_code)
    tokens = lexer.tokenize()

    # 语法分析
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print_ast(ast)        
        # 生成中间代码
        code_gen = CodeGenerator()
        ir_code = code_gen.generate(ast)
        print("\n中间代码:")
        print(ir_code)
        
        run_tac_program(ir_code)
    except ParserError as e:
        print(e)
