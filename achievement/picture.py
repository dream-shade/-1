import matplotlib.pyplot as plt

# 解决中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 数据配置
students = ['张三', '李四', '王五']
avg_scores = [89.67, 94.67, 92.00]
colors = ['#FF9999', '#66B3FF', '#99FF99']

# 绘制图表
plt.figure(figsize=(7, 5), dpi=300)
bars = plt.bar(students, avg_scores, color=colors, width=0.5)

# 图表细节配置
plt.title('三位学生平均成绩对比柱状图', fontsize=14)
plt.ylabel('平均成绩', fontsize=12)
plt.ylim(85, 100)

# 标注柱子顶部分数
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.3, f'{height:.2f}', ha='center', fontsize=11)

# 直接导出高清图片
plt.tight_layout()
plt.savefig('学生平均成绩柱状图.png')
plt.show()
