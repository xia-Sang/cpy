from typing import List

class Type:
    """基础类型类"""
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Type) and self.name == other.name

    def __repr__(self):
        return self.name

class ListType(Type):
    """列表类型，如 list<int>"""
    def __init__(self, element_type: Type):
        super().__init__(f'list<{element_type.name}>')
        self.element_type = element_type

    def __eq__(self, other):
        return isinstance(other, ListType) and self.element_type == other.element_type

    def __repr__(self):
        return f'list<{self.element_type}>'

class TupleType(Type):
    """元组类型，如 tuple<int, str, float>"""
    def __init__(self, element_types: List[Type]):
        elements = ', '.join([et.name for et in element_types])
        super().__init__(f'tuple<{elements}>')
        self.element_types = element_types

    def __eq__(self, other):
        return isinstance(other, TupleType) and self.element_types == other.element_types

    def __repr__(self):
        elements = ', '.join([str(et) for et in self.element_types])
        return f'tuple<{elements}>'
