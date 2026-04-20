class JavaRandom:
    """模拟 Java 的 java.util.Random（线性同余生成器）"""
    
    def __init__(self, seed: int):
        self.seed = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)
    
    def next(self, bits: int) -> int:
        self.seed = (self.seed * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        return self.seed >> (48 - bits)
    
    def nextInt(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("bound must be positive")
        
        if (bound & -bound) == bound:
            return (bound * self.next(31)) >> 31
        
        bits = self.next(31)
        val = bits % bound
        while bits - val + (bound - 1) < 0:
            bits = self.next(31)
            val = bits % bound
        return val
'''
(830, 12251)
'''

def to_int32(n: int) -> int:
    """模拟 Java 的 32 位有符号整数溢出"""
    n = n & 0xFFFFFFFF
    return n - 0x100000000 if n >= 0x80000000 else n


def is_slime_chunk(world_seed: int, chunk_x: int, chunk_z: int) -> bool:
    """检查指定区块是否为史莱姆区块"""
    seed = world_seed
    seed += to_int32(to_int32(chunk_x * chunk_x) * 4987142)
    seed += to_int32(chunk_x * 5947611)
    seed += to_int32(chunk_z * chunk_z) * 4392871
    seed += to_int32(chunk_z * 389711)
    seed ^= 987234911
    
    rng = JavaRandom(seed)
    return rng.nextInt(10) == 0


def is_slime_block(world_seed: int, block_x: int, block_z: int) -> bool:
    """检查指定坐标的方块是否为史莱姆块"""
    chunk_x = block_x // 16
    chunk_z = block_z // 16
    return is_slime_chunk(world_seed, chunk_x, chunk_z)


import math

def find_best_slime_farm_location(
    world_seed: int,
    center_x: int,
    center_z: int,
    search_radius: int,
    min_spawn_radius: int = 24,
    max_spawn_radius: int = 128,
    step: int = 1
) -> dict:
    """
    在指定圆形范围内搜索最佳的史莱姆农场位置
    
    Args:
        world_seed: 世界种子
        center_x, center_z: 搜索圆心坐标（方块坐标）
        search_radius: 搜索半径（从圆心开始搜索的范围）
        min_spawn_radius: 史莱姆最小生成距离（默认24格）
        max_spawn_radius: 史莱姆最大生成距离（默认128格）
        step: 搜索步长（默认1格，增大可加速但降低精度）
    
    Returns:
        包含最佳位置信息的字典
    """
    best_location = None
    max_slime_chunks = 0
    
    # 在搜索范围内遍历
    for dx in range(-search_radius, search_radius + 1, step):
        for dz in range(-search_radius, search_radius + 1, step):
            # 检查是否在搜索圆内
            if dx * dx + dz * dz > search_radius * search_radius:
                continue
            
            current_x = center_x + dx
            current_z = center_z + dz
            
            # 计算环形区域内的史莱姆区块数量
            slime_count = count_slime_chunks_in_ring(
                world_seed, current_x, current_z, 
                min_spawn_radius, max_spawn_radius
            )
            
            if slime_count > max_slime_chunks:
                max_slime_chunks = slime_count
                best_location = (current_x, current_z)
    
    return {
        'best_x': best_location[0] if best_location else center_x,
        'best_z': best_location[1] if best_location else center_z,
        'slime_chunk_count': max_slime_chunks,
        'center_x': center_x,
        'center_z': center_z,
        'search_radius': search_radius
    }


def count_slime_chunks_in_ring(
    world_seed: int, 
    center_x: int, 
    center_z: int,
    min_radius: int, 
    max_radius: int
) -> int:
    """
    计算环形区域内的史莱姆区块数量
    环形区域：min_radius 到 max_radius 之间的区域
    """
    count = 0
    
    # 计算需要检查的区块范围
    min_chunk_x = (center_x - max_radius) // 16
    max_chunk_x = (center_x + max_radius) // 16
    min_chunk_z = (center_z - max_radius) // 16
    max_chunk_z = (center_z + max_radius) // 16
    
    for chunk_x in range(min_chunk_x, max_chunk_x + 1):
        for chunk_z in range(min_chunk_z, max_chunk_z + 1):
            # 计算区块中心到玩家的距离
            block_x = chunk_x * 16 + 8  # 区块中心
            block_z = chunk_z * 16 + 8
            
            distance = math.sqrt(
                (block_x - center_x) ** 2 + (block_z - center_z) ** 2
            )
            
            # 检查是否在环形区域内
            if min_radius <= distance <= max_radius:
                if is_slime_chunk(world_seed, chunk_x, chunk_z):
                    count += 1
    
    return count


# 测试代码
if __name__ == "__main__":
    world_seed = 657965916
    center_x, center_z = -3098, 15119
    search_radius = 5000  # 在圆心周围50格内搜索
    
    print(f"正在搜索种子 {world_seed} 的最佳史莱姆农场位置...")
    print(f"搜索中心: ({center_x}, {center_z})")
    print(f"搜索半径: {search_radius} 格")
    print("-" * 50)
    
    result = find_best_slime_farm_location(
        world_seed, center_x, center_z, search_radius,
        min_spawn_radius=24, max_spawn_radius=128, step=4  # step=4 加速搜索
    )
    
    print(f"\n最佳位置: ({result['best_x']}, {result['best_z']})")
    print(f"环形区域内史莱姆区块数量: {result['slime_chunk_count']}")
    
    # 验证原始位置
    original_count = count_slime_chunks_in_ring(
        world_seed, center_x, center_z, 24, 128
    )
    print(f"\n对比 - 原始位置 ({center_x}, {center_z}) 的史莱姆区块数: {original_count}")
    print(f"优化提升: {result['slime_chunk_count'] - original_count} 个区块")