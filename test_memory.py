from memory import Memory

def test_basic_memory_operations():
    print("\n=== 测试基本内存操作 ===")
    mem = Memory()
    
    # 测试字写入和读取
    print("\n1. 测试字操作:")
    test_addr = 0x10000000
    test_value = 0x12345678
    mem.write_word(test_addr, test_value)
    value = mem.read_word(test_addr)
    print(f"写入: 0x{test_value:08x}, 读取: 0x{value:08x}")
    assert value == test_value, "字读写测试失败"
    
    # 测试字节操作
    print("\n2. 测试字节操作:")
    test_bytes = [0x41, 0x42, 0x43, 0x44]  # "ABCD"
    base_addr = 0x10000004
    
    # 写入字节
    for i, b in enumerate(test_bytes):
        mem.write_byte(base_addr + i, b)
    
    # 读取并验证
    for i, expected in enumerate(test_bytes):
        byte = mem.read_byte(base_addr + i)
        print(f"地址 0x{base_addr + i:08x}: 0x{byte:02x} ('{chr(byte)}')")
        assert byte == expected, f"字节读写测试失败 at offset {i}"

def test_stack_operations():
    print("\n=== 测试栈操作 ===")
    mem = Memory()
    
    # 压栈测试
    print("\n1. 压栈操作:")
    test_values = [0x11111111, 0x22222222, 0x33333333]
    stack_addresses = []
    
    for val in test_values:
        sp = mem.push_stack(val)
        stack_addresses.append(sp)
        print(f"压栈 0x{val:08x}, 栈指针: 0x{sp:08x}")
    
    # 出栈测试
    print("\n2. 出栈操作:")
    for i in range(len(test_values) - 1, -1, -1):
        val = mem.pop_stack()
        print(f"出栈值: 0x{val:08x}, 栈指针: 0x{mem.stack_pointer:08x}")
        assert val == test_values[i], "栈操作测试失败"

def test_heap_management():
    print("\n=== 测试堆内存管理 ===")
    mem = Memory()
    
    # 分配内存
    print("\n1. 内存分配测试:")
    test_sizes = [16, 32, 64, 128]
    allocated_addresses = []
    
    for size in test_sizes:
        addr = mem.malloc(size)
        allocated_addresses.append(addr)
        print(f"分配 {size} 字节, 地址: 0x{addr:08x}")
        # 写入一些测试数据
        mem.write_word(addr, size)
    
    mem.dump_heap_info()
    
    # 验证写入的数据
    for i, addr in enumerate(allocated_addresses):
        value = mem.read_word(addr)
        assert value == test_sizes[i], f"堆内存读写测试失败 at block {i}"
    
    # 释放内存
    print("\n2. 内存释放测试:")
    for addr in allocated_addresses[::2]:  # 释放偶数块
        mem.free(addr)
        print(f"释放地址: 0x{addr:08x}")
    
    mem.dump_heap_info()

def test_string_operations():
    print("\n=== 测试字符串操作 ===")
    mem = Memory()
    
    # 写入字符串
    test_strings = [
        "Hello, MIPS!",
        "测试中文",
        "Test\0Null\0Bytes",
        "!@#$%^&*()"
    ]
    
    base_addr = 0x10000000
    for i, test_str in enumerate(test_strings):
        addr = base_addr + i * 0x100
        print(f"\n1. 写入字符串 '{test_str}' 到地址 0x{addr:08x}")
        mem.write_string(addr, test_str)
        
        # 读取并验证
        read_str = mem.read_string(addr)
        print(f"2. 读取字符串: '{read_str}'")
        assert read_str == test_str.split('\0')[0], "字符串操作测试失败"
        
        # 打印内存内容
        print("3. 内存内容:")
        mem.dump_memory(addr, len(test_str) + 4)

def test_memory_protection():
    print("\n=== 测试内存保护 ===")
    mem = Memory()
    
    # 测试非对齐访问
    print("\n1. 测试非对齐内存访问:")
    unaligned_addresses = [0x10000001, 0x10000002, 0x10000003]
    for addr in unaligned_addresses:
        try:
            mem.write_word(addr, 0x12345678)
            assert False, f"应该抛出非对齐访问异常: 0x{addr:08x}"
        except Exception as e:
            print(f"预期的错误 at 0x{addr:08x}: {e}")
    
    # 测试内存越界
    print("\n2. 测试内存越界:")
    addr = mem.malloc(16)
    try:
        mem.write_word(addr + 16, 0x12345678)  # 写入已分配区域之外
        assert False, "应该抛出内存越界异常"
    except Exception as e:
        print(f"预期的错误: {e}")
    
    # 测试重复释放
    print("\n3. 测试重复释放:")
    mem.free(addr)
    try:
        mem.free(addr)
        assert False, "应该抛出重复释放异常"
    except Exception as e:
        print(f"预期的错误: {e}")

if __name__ == "__main__":
    try:
        test_basic_memory_operations()
        print("基本内存操作测试通过")
        
        test_stack_operations()
        print("栈操作测试通过")
        
        test_heap_management()
        print("堆管理测试通过")
        
        test_string_operations()
        print("字符串操作测试通过")
        
        test_memory_protection()
        print("内存保护测试通过")
        
        print("\n所有测试通过!")
    except AssertionError as e:
        print(f"测试失败: {e}")
    except Exception as e:
        print(f"测试过程中出现错误: {e}") 