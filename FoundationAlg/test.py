from NewFoundationPit import *

from typing import List

# 创建 ConcreteMaterial 对象
# (name)、重度 (gamma)、弹性模量 (E)、泊松比 (v)，以及可选的剪切模量 (G)
concrete = ConcreteMaterial(name='C40 混凝土',gamma=25,E=60000000000,v=0.3)


# 创建左右地下连续墙对象

left_wall = UndergroundDiaphragmWall(L=16.4,h=1, material=concrete)
right_wall = UndergroundDiaphragmWall(L=16.4,h=1, material=concrete)

# 创建 SupportMaterial 对象
support_material = SupportMaterial(
    name='混凝土支撑',
    gamma=25000,  # 重度，单位 kg/m³
    E=1000000000,  # 弹性模量，单位 Pa
    A=1  # 横截面积，单位 m²（具体含义取决于应用场景）
)

# support_material2 = SupportMaterial(
#     name='Reinforced Concrete',
#     gamma=2600,  # 重度，单位 kg/m³
#     E=30e9,  # 弹性模量，单位 Pa
#     A=0.1  # 横截面积，单位 m²（具体含义取决于应用场景）
# )

# 创建水平支撑对象列表
supports = [
    HorizontalSupport(
        material=support_material,
        spaceLength=46.9  # 支撑间距，单位 m
    ),
    # HorizontalSupport(
    #     material=support_material2,
    #     spaceLength=3.0  # 支撑间距，单位 m
    # )
    # 添加更多支撑，根据需要
]



soil1 = SoilMaterial(
    name='Mudstone',
    gamma=25900,  # 重度，单位 kg/m³
    E=100000000,      # 弹性模量，单位 Pa
    phi=30,      # 内摩擦角，单位度
    c=300,        # 粘聚力，单位 kPa（注意单位转换，如果 gamma 是 kg/m³，则 c 应该是 kN/m² 或 kPa）
    sandy=True
)

# soil2 = SoilMaterial(
#     name='Sand',
#     gamma=1800,  # 重度，单位 kg/m³
#     E=50e6,      # 弹性模量，单位 Pa
#     phi=30,      # 内摩擦角，单位度
#     c=10,        # 粘聚力，单位 kPa（注意单位转换，如果 gamma 是 kg/m³，则 c 应该是 kN/m² 或 kPa）
#     sandy=True
# )
#
# soil3 = SoilMaterial(
#     name='Gravel',
#     gamma=1800,  # 重度，单位 kg/m³
#     E=50e6,      # 弹性模量，单位 Pa
#     phi=30,      # 内摩擦角，单位度
#     c=10,        # 粘聚力，单位 kPa（注意单位转换，如果 gamma 是 kg/m³，则 c 应该是 kN/m² 或 kPa）
#     sandy=True
# )

# 土壤层间隔信息，每个字典代表一个层，包含顶部和底部深度（或其他定义间隔的方式）
intervals = [
    {'top': 0, 'bottom': 16.4},  # 第一层从地表开始，到5米深
    # {'top': 5, 'bottom': 10},  # 第二层从5米深开始，到10米深
    # {'top': 10, 'bottom': 15}  # 第三层从10米深开始，到15米深
]

bore_hole = BoreHole(soils=[soil1], intervals=intervals)

# 创建 FoundationPit 对象
foundation_pit = FoundationPit(
    left_wall=left_wall,
    right_wall=right_wall,
    H1=15.0,  # 左侧开挖深度
    H2=20.0,  # 右侧开挖深度
    supports=supports,
    support_count=len(supports),  # 或者直接写为数字，如果已知
    ds=[0],  # 或者提供一个具体的列表，如果已知
    B=46.9,  # 基坑开挖宽度
    D=1,  # 基坑计算厚度，一般取 1
    bore_hole=bore_hole,
    Palim=0.005,
    Pplim=0.05,
    left_over_load=10000,  # 左侧基坑超载（Pa）
    right_over_load=10000,  # 右侧基坑超载（Pa）
    left_strength_load=30000,  # 左侧基坑加固（Pa）
    right_strength_load=30000  # 右侧基坑加固（Pa）
)

# 假设这是你的字典列表
dict_list = [
    {'name': '2', 'gamma': 2.0, 'E': 2.0, 'A': 2.0, 'spaceLength': 2.0},
    {'name': '3', 'gamma': 3.0, 'E': 3.0, 'A': 3.0, 'spaceLength': 3.0}
]

# 创建水平支撑对象列表
supports = []

for item in dict_list:
    # 从字典中提取参数
    material_params = {
        'name': item['name'],
        'gamma': item['gamma'],
        'E': item['E'],
        'A': item['A']
    }
    spaceLength = item['spaceLength']

    # 创建 SupportMaterial 对象
    material = SupportMaterial(**material_params)

    # 创建 HorizontalSupport 对象并添加到列表中
    support = HorizontalSupport(material=material, spaceLength=spaceLength)
    supports.append(support)

# # 输出结果以验证
# for support in supports:
#     print(f"Support Material: {support.Material.name}, Space Length: {support.SpaceLength}")


print(foundation_pit)

# print(foundation_pit)
# # 假设 UndergroundDiaphragmWall 类有以下属性：L, h, material（其中 material 又有 name 属性）
# print(f"Left Wall Info:")
# print(f"  Length (L): {left_wall.L}")
# print(f"  Height (h): {left_wall.h}")
# print(f"  Material Name: {left_wall.material.name}")

#
# if foundation_pit.bore_hole.soils:  # 检查列表是否为空
#     soil1_dict = foundation_pit.bore_hole.soils[1]  # 获取第一个字典
#     soil1_info = soil1_dict['soil']  # 从字典中获取 SoilMaterial 对象
#     if soil1_info:  # 检查是否成功获取了 SoilMaterial 对象
#         print(f"土壤名称: {soil1_info.name}")
#         print(f"重度: {soil1_info.gamma} kg/m³")
#         print(f"弹性模量: {soil1_info.E} Pa")
#         print(f"内摩擦角: {soil1_info.phi} 度")
#         print(f"粘聚力: {soil1_info.c} kPa")
#     else:
#         print("第一个土壤字典中没有 'soil' 键或对应的值不是 SoilMaterial 对象。")
# else:
#     print("没有土壤信息可供输出。")



