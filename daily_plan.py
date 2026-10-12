tasks=[]
hours=float(input("今日任务时长"))
n=int(input("任务数量"))
for i in range(n):
    name=input(f"第{i+1}项任务名称")
    weight=float(input("任务权重"))
    tasks.append((name,weight))
total=sum(w for _, w in tasks)
print("\n今日计划")
for name,w in tasks:
    print(f"{name}:{hours*w/total:.1f}小时")
with open("plan.txt","w",encoding="utf-8") as f:
    f.write(f"{name}:{hours*w/total:.1f}小时")

