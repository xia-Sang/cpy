from ast_nodes import print_ast
from command import process_file
import sys
import parser
from semantic import SemanticAnalyzer, SemanticError

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python main.py [-a|-g|-l] <源代码文件>")
        print("选项:")
        print("  -a    显示抽象语法树")
        print("  -g    显示生成的中间代码")
        print("  -l    显示词法分析结果")
        print("  --debug 启用调试模式")
        sys.exit(1)

    # 创建命令行参数对象
    class Args:
        def __init__(self, a=False, g=False, l=False, debug=False):
            self.a = a
            self.g = g
            self.l = l
            self.debug = debug

    # 解析命令行参数
    args = Args()
    filename = None

    for arg in sys.argv[1:]:
        if arg.startswith('-'):
            if arg == '-a': args.a = True
            elif arg == '-g': args.g = True
            elif arg == '-l': args.l = True
            elif arg == '--debug': args.debug = True
        else:
            filename = arg

    if not filename:
        print("错误: 未指定源代码文件")
        sys.exit(1)

    process_file(filename, args)

    ast = parser.parse()
    
    # 添加语义分析
    semantic_analyzer = SemanticAnalyzer()
    try:
        semantic_analyzer.analyze(ast)
        print("语义分析通过")
    except SemanticError as e:
        print(e)
        sys.exit(1)
        
    if args.a:
        print_ast(ast)
