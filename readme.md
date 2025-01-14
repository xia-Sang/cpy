# Simple Programming Language Implementation
[中文版](./readme_zh.md)
A simple programming language implementation including lexical analysis, syntax analysis, semantic analysis, and virtual machine execution.

## Features

### Basic Types
- nil: Empty/null type
- bool: Boolean type (true/false)
- int: Integer type
- float: Floating-point type
- str: String type

### Compound Types
- list<T>: Generic list type
  - Supports generic type parameters
  - Array-like access and modification
  - Example: `list<int> nums = [1, 2, 3]`

- tuple<T1, T2, ...>: Tuple type
  - Supports multiple type parameters
  - Indexed access
  - Immutable
  - Example: `tuple<int, str> pair = (1, "hello")`

### Functions
```python
fn add(x: int, y: int) -> int {
    return x + y;
}

fn greet(name: str) -> void {
    print("Hello, " + name);
}
```

- Multiple parameter support
- Return type declaration
- Nested function calls
- Recursive calls

### Control Flow
- Conditional Statements
```python
if (condition) {
    // code
} elif (another_condition) {
    // code
} else {
    // code
}
```

- Loops
```python
for (int i = 0; i < 10; i = i + 1) {
    // code
}
```

- Loop Control
  - break
  - continue

### Variables and Assignment
- Variable declaration and initialization
- Type inference
- Array/List element assignment
- Read-only tuple access

### Operators
- Arithmetic: +, -, *, /, %
- Comparison: ==, !=, <, >, <=, >=
- Logical: &&, ||, !

### Built-in Functions
- print(): Output to console
- input(): Read user input

## Technical Implementation

### 1. Compiler Architecture
- Lexical Analyzer (lexer.py)
  - Converts source code to token stream
  - Handles keywords, identifiers, operators

- Syntax Analyzer (parser.py)
  - Builds Abstract Syntax Tree (AST)
  - Complex type declarations
  - Expression parsing

- Code Generator (code_generator.py)
  - Generates intermediate code
  - Handles array and tuple operations

- Virtual Machine (virtual_machine.py)
  - Stack-based architecture
  - Function call conventions
  - Basic memory management

### 2. Command Line Usage
```bash
python main.py [options] filename

Options:
  -l         Show lexical analysis results
  -a         Show abstract syntax tree
  -g         Show generated intermediate code
  --debug    Enable debug mode
```

## Example Code

```python
fn factorial(n: int) -> int {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

fn main() -> int {
    int result = factorial(5);
    print(result);
    return 0;
}
```

## Development Roadmap

- [ ] Enhanced Standard Library
  - More built-in functions
  - File I/O operations
  - Mathematical functions

- [ ] Type System Improvements
  - Class support
  - Interface/trait system
  - Type checking enhancements

- [ ] Performance Optimization
  - Improved virtual machine
  - Code optimization passes
  - Memory management

- [ ] Language Features
  - Exception handling
  - Module system
  - Multi-threading support

## Requirements & Limitations

### Requirements
- Python 3.6+
- UTF-8 encoding support

### Current Limitations
- Limited function parameter count
- No multi-threading support
- Basic type system
- Limited standard library

### Debugging
- Set `vm.debug = True` for detailed execution logging
- View stack and register states
- Trace function calls

## Notes
- This is a learning-focused implementation
- Suitable for educational purposes
- Basic but functional compiler implementation
- Future improvements planned

