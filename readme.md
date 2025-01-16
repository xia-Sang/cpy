# 简单编程语言实现 
> 学习编译原理完毕之后简单实现，并不完善-后续可能会更进
这个项目实现了一个支持基本编程功能的编译器和虚拟机系统。

## 语言特性

### 1. 数据类型系统

#### 基本类型
- nil: 空值类型
- bool: 布尔类型 (true/false)
- int: 整数类型
- float: 浮点数类型
- str: 字符串类型

#### 复合类型
- list<T>: 泛型列表类型
  ```python
  list<int> numbers = [1, 2, 3];
  list<str> names = ["Alice", "Bob"];
  ```

- tuple<T1,T2,...>: 元组类型
  ```python
  tuple<int, str> pair = (1, "hello");
  tuple<float, bool, str> triple = (3.14, true, "world");
  ```

### 2. 变量声明和操作

#### 变量声明
```python
int x = 10;
str name = "John";
list<int> numbers = [1, 2, 3];
```

#### 变量访问和修改
- 支持基本赋值操作
- 支持复合赋值操作 (+=, -=, *=, /=)
- 支持数组/列表下标访问

### 3. 函数系统

#### 函数定义
```python
fn add(x: int, y: int) -> int {
    return x + y;
}

fn greet(name: str) -> void {
    print("Hello, " + name);
}
```

#### 函数特性
- 支持多个参数
- 支持不同返回类型
- 支持函数嵌套调用
- 支持递归调用

### 4. 类和对象系统
>目前仅仅定义 但不支持
#### 类定义
```python
class Person {
    str name;
    int age;
    
    fn getName() -> str {
        return this.name;
    }
}
```

#### 类特性
- 支持成员变量
- 支持成员方法
- 支持访问控制（public/private）
- 支持继承（使用[]语法）

### 5. 控制流语句

#### 条件语句
```python
if (condition) {
    // code
} elif (another_condition) {
    // code
} else {
    // code
}
```

#### 循环语句
```python
for (int i = 0; i < 10; i=i+1) {
    // code
}
```

#### 循环控制
- break: 跳出循环
- continue: 继续下一次循环

### 6. 运算符系统

#### 算术运算符
- +, -, *, /, % , ++ , --

#### 比较运算符
- ==, !=, <, >, <=, >= 

#### 逻辑运算符
- &&（与）
- ||（或）
- !（非）

## 技术实现

### 1. 编译器架构
- 词法分析器   
- 语法分析器   
- AST生成器    
- 中间代码生成器  
- 虚拟机运行

### 2. 简单虚拟机实现 
> 后续补充完善函数调用栈模型
- 基于栈的虚拟机
- 函数调用约定

## 使用示例

1. 创建源代码文件 `code.cpy`:
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

2. 运行编译器和虚拟机：
```bash
python main.py code.cpy
```

## 开发计划

- [ ] 添加更多标准库函数
- [ ] 实现更完整的类型系统
- [ ] 添加异常处理机制
- [ ] 优化虚拟机性能
- [ ] 添加模块导入系统

## 注意事项

1. 环境要求
   - Python 3.6+
   - UTF-8编码支持

2. 限制
   - 函数参数数量限制
   - 不支持多线程
   - 部分复杂类型操作可能受限

3. 调试
   - 设置 `vm.debug = True` 开启调试模式
   - 查看详细的执行过程和状态