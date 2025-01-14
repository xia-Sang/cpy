class MemoryBlock:
    """内存块结构"""
    def __init__(self, start, size, is_free=True):
        self.start = start      # 起始地址
        self.size = size        # 大小（字节）
        self.is_free = is_free  # 是否空闲
        self.next = None        # 下一个内存块

class Memory:
    def __init__(self):
        self.memory = {}  # 内存数据
        # 内存段基址
        self.TEXT_BASE = 0x00400000   # 代码段起始地址
        self.DATA_BASE = 0x10000000   # 数据段起始地址
        self.HEAP_BASE = 0x10040000   # 堆基址
        self.STACK_BASE = 0x7FFFFF00  # 修改：确保栈基址是4字节对齐的
        
        # 初始化堆内存管理
        self.heap_start = self.HEAP_BASE
        self.heap_size = 0x10000  # 64KB初始堆大小
        self.free_blocks = MemoryBlock(self.heap_start, self.heap_size)
        
        # 栈指针，确保初始值是4字节对齐的
        self.stack_pointer = self.STACK_BASE & ~0x3

    def read_word(self, addr):
        """读取一个字（4字节）"""
        if addr & 0x3:  # 检查地址对齐
            raise Exception(f"Unaligned memory access at 0x{addr:08x}")
        return self.memory.get(addr, 0)

    def write_word(self, addr, value):
        """写入一个字（4字节）"""
        if addr & 0x3:  # 检查地址对齐
            raise Exception(f"Unaligned memory access at 0x{addr:08x}")
        self.memory[addr] = value & 0xFFFFFFFF

    def read_byte(self, addr):
        """读取一个字节"""
        word = self.read_word(addr & ~0x3)
        offset = addr & 0x3
        return (word >> ((3 - offset) * 8)) & 0xFF

    def write_byte(self, addr, value):
        """写入一个字节"""
        word_addr = addr & ~0x3
        offset = addr & 0x3
        old_word = self.read_word(word_addr)
        mask = ~(0xFF << ((3 - offset) * 8))
        new_word = (old_word & mask) | ((value & 0xFF) << ((3 - offset) * 8))
        self.write_word(word_addr, new_word)

    def malloc(self, size):
        """分配内存（首次适应算法）"""
        # 对齐到4字节
        size = (size + 3) & ~0x3
        
        current = self.free_blocks
        while current:
            if current.is_free and current.size >= size:
                if current.size > size:
                    # 分割内存块
                    new_block = MemoryBlock(current.start + size, 
                                          current.size - size)
                    new_block.next = current.next
                    current.size = size
                    current.next = new_block
                
                current.is_free = False
                return current.start
            current = current.next
            
        # 没有足够的空闲内存
        raise Exception("Out of memory")

    def free(self, addr):
        """释放内存"""
        current = self.free_blocks
        while current:
            if current.start == addr:
                if not current.is_free:
                    current.is_free = True
                    # 合并相邻的空闲块
                    self._merge_free_blocks()
                    return
                else:
                    raise Exception("Double free detected")
            current = current.next
        raise Exception("Invalid free address")

    def _merge_free_blocks(self):
        """合并相邻的空闲块"""
        current = self.free_blocks
        while current and current.next:
            if current.is_free and current.next.is_free:
                # 合并相邻的空闲块
                current.size += current.next.size
                current.next = current.next.next
            else:
                current = current.next

    def push_stack(self, value):
        """压栈（确保4字节对齐）"""
        # 确保栈指针减少后仍然是4字节对齐的
        new_sp = (self.stack_pointer - 4) & ~0x3
        if new_sp < self.HEAP_BASE:  # 检查栈溢出
            raise Exception("Stack overflow")
        self.stack_pointer = new_sp
        self.write_word(self.stack_pointer, value)
        return self.stack_pointer

    def pop_stack(self):
        """出栈（确保4字节对齐）"""
        if self.stack_pointer >= self.STACK_BASE:
            raise Exception("Stack underflow")
        value = self.read_word(self.stack_pointer)
        self.stack_pointer = (self.stack_pointer + 4) & ~0x3
        return value

    def dump_memory(self, start_addr, size):
        """打印内存内容（支持UTF-8显示）"""
        print("\nMemory Dump:")
        for i in range(0, size, 16):
            addr = start_addr + i
            values = []
            chars = []
            bytes_data = bytearray()
            
            for j in range(16):
                curr_addr = addr + j
                if curr_addr in self.memory:
                    byte = self.read_byte(curr_addr)
                    values.append(f"{byte:02x}")
                    bytes_data.append(byte)
                else:
                    values.append("--")
            
            # 尝试将字节序列解码为字符串
            try:
                text = bytes_data.decode('utf-8')
                chars = [c if 32 <= ord(c) <= 126 or ord(c) > 127 else '.' for c in text]
            except UnicodeDecodeError:
                chars = ['.' for _ in bytes_data]
            
            hex_str = ' '.join(values)
            char_str = ''.join(chars)
            print(f"0x{addr:08x}: {hex_str:<48} {char_str}")

    def dump_heap_info(self):
        """打印堆内存信息"""
        print("\nHeap Memory Info:")
        current = self.free_blocks
        while current:
            status = "FREE" if current.is_free else "USED"
            print(f"Block at 0x{current.start:08x}, "
                  f"size={current.size}, status={status}")
            current = current.next 

    def read_string(self, addr):
        """从内存中读取以null结尾的字符串"""
        bytes_data = bytearray()
        current_addr = addr
        while True:
            byte = self.read_byte(current_addr)
            if byte == 0:  # 遇到null终止符
                break
            bytes_data.append(byte)
            current_addr += 1
        try:
            return bytes_data.decode('utf-8')
        except UnicodeDecodeError:
            return bytes_data.decode('latin1')  # 回退到单字节编码

    def write_string(self, addr, string):
        """将字符串写入内存（包括null终止符）"""
        current_addr = addr
        # 将字符串转换为UTF-8字节序列
        bytes_data = string.encode('utf-8')
        
        # 写入字符串内容
        for byte in bytes_data:
            self.write_byte(current_addr, byte)
            current_addr += 1
        
        # 写入null终止符
        self.write_byte(current_addr, 0)
        return current_addr - addr + 1  # 返回写入的总字节数（包括null终止符）

    def read_string_fixed(self, addr, max_length):
        """读取固定长度的字符串（用于带长度限制的读取）"""
        bytes_data = bytearray()
        for i in range(max_length):
            byte = self.read_byte(addr + i)
            if byte == 0:
                break
            bytes_data.append(byte)
        try:
            return bytes_data.decode('utf-8')
        except UnicodeDecodeError:
            return bytes_data.decode('latin1')

    def write_string_fixed(self, addr, string, max_length):
        """写入固定长度的字符串（确保不超过指定长度）"""
        bytes_data = string.encode('utf-8')
        
        # 确保字节序列不超过最大长度（包括null终止符）
        if len(bytes_data) >= max_length:
            # 尝试找到有效的UTF-8边界
            while len(bytes_data) >= max_length:
                try:
                    bytes_data[:(max_length-1)].decode('utf-8')
                    break
                except UnicodeDecodeError:
                    max_length -= 1
            bytes_data = bytes_data[:(max_length-1)]
        
        # 写入字符串内容
        current_addr = addr
        for byte in bytes_data:
            self.write_byte(current_addr, byte)
            current_addr += 1
        
        # 写入null终止符
        self.write_byte(current_addr, 0)
        current_addr += 1
        
        # 用0填充剩余空间
        while current_addr < addr + max_length:
            self.write_byte(current_addr, 0)
            current_addr += 1

    def check_string_bounds(self, addr, max_length=None):
        """检查字符串操作的边界"""
        if addr < self.DATA_BASE or addr >= self.HEAP_BASE:
            raise Exception(f"String address out of bounds: 0x{addr:08x}")
        
        if max_length is not None:
            end_addr = addr + max_length
            if end_addr >= self.HEAP_BASE:
                raise Exception(f"String length exceeds memory bounds: {max_length}")

    def get_string_length(self, addr):
        """获取字符串长度（到null终止符为止）"""
        length = 0
        while self.read_byte(addr + length) != 0:
            length += 1
            if length > 1024:  # 防止无限循环
                raise Exception("String too long or missing null terminator")
        return length 