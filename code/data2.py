#根据模型‘lte020-0.0-0.0.BT-Settl.7.dat.xml’画图，画了一个对数形式的图


from astropy.io import votable
import matplotlib.pyplot as plt
def parse_votable(file_path):
    # 读取 VOTable 文件
    vot = votable.parse(file_path)
    
    # 获取第一个表
    table = vot.get_first_table()
    
    # # 打印表中的数据
    # for row in table.array:
    #     print(row)
    return table


def plot_data(data):
    # 提取横坐标和纵坐标
    x_values = [item[0] for item in data]  # 提取每个子数组的第一个元素作为 x 值
    y_values = [item[1] for item in data]  # 提取每个子数组的第二个元素作为 y 值

    # 绘图
    plt.figure(figsize=(10, 6))  # 设置图形大小
    plt.plot(x_values, y_values, marker='o', linestyle='-')  # 绘制折线图，并用圆圈标记每个点

    # 添加标题和坐标轴标签
    plt.title('Plot of Data Points')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    # 显示网格
    plt.grid(True)

    # 显示图形
    plt.show()

def plot_loglog(data):
    # 提取横坐标和纵坐标
    x_values = [item[0] for item in data]  # 提取每个子数组的第一个元素作为 x 值
    y_values = [item[1] for item in data]  # 提取每个子数组的第二个元素作为 y 值

    # 绘制对数图
    plt.figure(figsize=(10, 6))  # 设置图形大小
    plt.loglog(x_values, y_values, marker='o', linestyle='-', color='blue')  # 使用对数刻度绘制折线图

    # 添加标题和坐标轴标签
    plt.title('Log-Log Plot of Data Points')
    plt.xlabel('X-axis (log scale)')
    plt.ylabel('Y-axis (log scale)')

    # 显示网格
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # 显示图形
    plt.show()

# 示例用法
table=parse_votable('models/bt-settl_55.dat.xml')
print(table.array.shape)
#plot_data(table.array[::100])
plot_loglog(table.array[::100])