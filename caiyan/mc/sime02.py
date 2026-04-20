class JavaRandom:
    """模拟 Java 的 java.util.Random（线性同余生成器）"""
    
    def __init__(self, seed: int):
        # Java Random 对种子进行初始扰乱：与 0x5DEECE66D 异或并取低48位
        self.seed = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)
    
    def next(self, bits: int) -> int:
        """生成指定位数的随机数（最多31位）"""
        self.seed = (self.seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        return self.seed >> (48 - bits)
    
    def nextInt(self, bound: int) -> int:
        """生成 [0, bound) 范围内的随机整数，与 Java 的拒绝采样逻辑一致"""
        if bound <= 0:
            raise ValueError("bound must be positive")
        
        # 对于2的幂次，使用位运算优化（快速路径）
        if (bound & -bound) == bound:
            return (bound * self.next(31)) >> 31
        
        # 拒绝采样，确保均匀分布
        bits = self.next(31)
        val = bits % bound
        # 如果结果会偏向小的数值，则拒绝并重新生成
        while bits - val + (bound - 1) < 0:
            bits = self.next(31)
            val = bits % bound
        return val


def to_int32(n: int) -> int:
    """模拟 Java 的 32 位有符号整数溢出"""
    n = n & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n


def is_slime_chunk(world_seed: int, chunk_x: int, chunk_z: int) -> bool:
    """
    检查指定区块是否为史莱姆区块（Minecraft Java版算法）
    
    Args:
        world_seed: 世界种子（64位整数，可通过 /seed 获取）
        chunk_x: 区块 X 轴坐标（32位整数）
        chunk_z: 区块 Z 轴坐标（32位整数）
    
    Returns:
        如果是史莱姆区块返回 True，否则返回 False
    """
    # 按照 Java 代码的运算顺序和类型转换规则计算种子
    # 注意：中间乘法运算遵循 Java int（32位）的溢出规则
    
    seed = world_seed
    # (long)(chunkX * chunkX * 4987142)
    seed += to_int32(to_int32(chunk_x * chunk_x) * 4987142)
    # (long)(chunkX * 5947611)
    seed += to_int32(chunk_x * 5947611)
    # (long)(chunkZ * chunkZ) * 4392871L
    seed += to_int32(chunk_z * chunk_z) * 4392871
    # (long)(chunkZ * 389711)
    seed += to_int32(chunk_z * 389711)
    # ^ 987234911L
    seed ^= 987234911
    
    rng = JavaRandom(seed)
    return rng.nextInt(10) == 0

def is_slime_block(world_seed: int, block_x: int, block_z: int) -> bool:
    """检查指定坐标的方块是否为史莱姆块"""
    chunk_x = block_x // 16
    chunk_z = block_z // 16
    return is_slime_chunk(world_seed, chunk_x, chunk_z)

# 示例用法
if __name__ == "__main__":
    # 测试：种子 12345，检查 (0,0) 区块
    world_seed = 657965916
    x,y=-5304,18467
    if is_slime_block(world_seed, x, y):
        print(f"坐标 ({x}, {y}) 是史莱姆块！")
    else:
        print(f"坐标 ({x}, {y}) 不是史莱姆块。")
