import matplotlib.pyplot as plt
import matplotlib.patches as patches

def visualize_slime_farm_area(
    world_seed: int,
    center_x: int,
    center_z: int,
    min_radius: int = 24,
    max_radius: int = 128,
    title: str = ""
):
    """可视化史莱姆农场区域的区块分布"""
    
    fig, ax = plt.subplots(figsize=(12, 12))
    
    # 计算需要显示的区块范围
    padding = 16
    min_chunk_x = (center_x - max_radius - padding) // 16
    max_chunk_x = (center_x + max_radius + padding) // 16
    min_chunk_z = (center_z - max_radius - padding) // 16
    max_chunk_z = (center_z + max_radius + padding) // 16
    
    slime_chunks = []
    normal_chunks = []
    
    # 收集区块信息
    for chunk_x in range(min_chunk_x, max_chunk_x + 1):
        for chunk_z in range(min_chunk_z, max_chunk_z + 1):
            block_x = chunk_x * 16 + 8
            block_z = chunk_z * 16 + 8
            
            distance = math.sqrt(
                (block_x - center_x) ** 2 + (block_z - center_z) ** 2
            )
            
            is_in_ring = min_radius <= distance <= max_radius
            
            if is_slime_chunk(world_seed, chunk_x, chunk_z):
                slime_chunks.append((chunk_x, chunk_z, is_in_ring))
            else:
                normal_chunks.append((chunk_x, chunk_z, is_in_ring))
    
    # 绘制普通区块（淡色）
    for cx, cz, in_ring in normal_chunks:
        color = '#E8E8E8' if in_ring else '#F5F5F5'
        edgecolor = '#CCCCCC' if in_ring else '#E0E0E0'
        # Z轴翻转：cz * 16 变成 -cz * 16
        rect = patches.Rectangle(
            (cx * 16, -cz * 16), 16, -16,
            linewidth=0.5, edgecolor=edgecolor, facecolor=color
        )
        ax.add_patch(rect)
    
    # 绘制史莱姆区块（绿色）
    for cx, cz, in_ring in slime_chunks:
        if in_ring:
            # 环形区域内的史莱姆区块（深绿色，重要）
            color = '#2E7D32'
            edgecolor = '#1B5E20'
            linewidth = 2
        else:
            # 环形区域外的史莱姆区块（浅绿色）
            color = '#A5D6A7'
            edgecolor = '#81C784'
            linewidth = 0.5
        
        # Z轴翻转
        rect = patches.Rectangle(
            (cx * 16, -cz * 16), 16, -16,
            linewidth=linewidth, edgecolor=edgecolor, facecolor=color
        )
        ax.add_patch(rect)
    
    # 绘制环形区域边界
    inner_circle = plt.Circle(
        (center_x, -center_z), min_radius, 
        fill=False, color='red', linestyle='--', linewidth=2, label='24格边界'
    )
    outer_circle = plt.Circle(
        (center_x, -center_z), max_radius, 
        fill=False, color='blue', linestyle='--', linewidth=2, label='128格边界'
    )
    ax.add_patch(inner_circle)
    ax.add_patch(outer_circle)
    
    # 标记中心点
    ax.plot(center_x, -center_z, 'r+', markersize=20, mew=2, label='农场中心')
    
    # 设置坐标轴（Z轴向下为负）
    ax.set_xlim(min_chunk_x * 16, (max_chunk_x + 1) * 16)
    ax.set_ylim(-(max_chunk_z + 1) * 16, -min_chunk_z * 16)  # Y轴翻转
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    # 统计信息
    ring_slime = sum(1 for _, _, in_ring in slime_chunks if in_ring)
    total_slime = len(slime_chunks)
    
    ax.set_title(
        f'{title}\n种子: {world_seed} | 中心: ({center_x}, {center_z})\n'
        f'环形区域内史莱姆区块: {ring_slime} / 总史莱姆区块: {total_slime}',
        fontsize=12
    )
    
    plt.xlabel('X 坐标（方块）')
    plt.ylabel('Z 坐标（方块，向下为负）')
    plt.tight_layout()
    plt.show()
    
    return ring_slime

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


# 对比可视化：原始位置 vs 最佳位置
world_seed = 657965916
#center_x, center_z = 830,12251

# 先找到最佳位置
# result = find_best_slime_farm_location(
#     world_seed, center_x, center_z, 50,
#     min_spawn_radius=24, max_spawn_radius=128, step=4
# )

best_x, best_z = -5357,18408

print("=" * 60)
# print("原始位置可视化:")
# original_count = visualize_slime_farm_area(
#     world_seed, center_x, center_z,
#     title="原始位置"
# )

print("\n" + "=" * 60)
print("优化后位置可视化:")
best_count = visualize_slime_farm_area(
    world_seed, best_x, best_z,
    title="优化后位置"
)
