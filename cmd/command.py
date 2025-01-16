from codegenerator.codegen import CodeGenerator
from lexer import Lexer
from parser.parser import Parser
from parser.print_ast import print_ast
from vm.simple_vm import run_tac_program
def process_file(filepath: str, args) -> None:
    """处理源代码文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"错误: 未找到文件 '{filepath}'")
        return
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return

    # 词法分析
    lexer = Lexer(source_code)
    try:
        tokens = lexer.tokenize()
        if args.l:  # -l 选项：显示词法分析结果
            print("\n=== 词法分析结果 ===")
            for token in tokens:
                print(token)
            return
    except Exception as e:
        print(f"词法分析错误: {e}")
        return

    # 语法分析
    parser = Parser(tokens)
    try:
        ast = parser.parse()
        if args.a:  # -a 选项：显示语法树
            print("\n=== 抽象语法树 ===")
            print_ast(ast)
            return
    except Exception as e:
        print(f"语法分析错误: {e}")
        return

    # 生成中间代码
    code_gen = CodeGenerator()
    try:
        ir_code = code_gen.generate(ast)
        if args.g:  # -g 选项：显示中间代码
            print("\n=== 中间代码 ===")
            print(ir_code)
            return
    except Exception as e:
        print(f"代码生成错误: {e}")
        return

    # 默认执行代码
    try:
       run_tac_program(ir_code, debug=args.debug)
    except Exception as e:
        print(f"执行错误: {e}")

