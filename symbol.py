# symbol.py

from typing import Dict, List, Optional, Tuple
from typ import Type

class Symbol:
    """符号表项"""
    def __init__(self, 
                 name: str, 
                 symbol_type: str, 
                 data_type: Type,
                 is_function: bool = False,
                 params: List[Tuple[str, Type]] = None,
                 is_variadic: bool = False):  # 添加可变参数标志
        self.name = name
        self.symbol_type = symbol_type  # 'variable', 'function', 'class', etc.
        self.data_type = data_type
        self.is_function = is_function
        self.params = params if params is not None else []
        self.is_variadic = is_variadic  # 是否是可变参数函数
    
    def __str__(self):
        return f"Symbol(name='{self.name}', type='{self.symbol_type}', data_type='{self.data_type}')"

class SymbolTable:
    """符号表，支持嵌套作用域"""
    def __init__(self, parent: Optional['SymbolTable'] = None):
        self.symbols: Dict[str, Symbol] = {}
        self.parent = parent

    def define(self, symbol: Symbol):
        if symbol.name in self.symbols:
            raise Exception(f"Symbol '{symbol.name}' already defined in current scope.")
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        symbol = self.symbols.get(name)
        if symbol:
            return symbol
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None
