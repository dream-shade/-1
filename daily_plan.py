def calculate_plan():
    # 1. 初始化变量
    # 注意：input 获取的是字符串，计算需要转换为 float
    hours = float(input("输入总时长: "))
    tasks = []
    i = 0  # 计数器放在循环外面，防止每次都被重置为 0

    try:
        while True:
            # 2. 循环收集任务信息
            name = input(f"第{i+1}项任务名称 (输入'结束'退出): ")

            # 设置退出条件
            if name == "结束":
                break

            weight = float(input("任务权重: "))
            order=int(input("任务顺序"))
            tasks.append((name, weight,order))

            i += 1  # 计数器加 1 (注意语法是 +=)

        # 3. 循环结束后，统一进行计算和保存
        if tasks:  # 防止没有输入任务时除数为 0 报错
            total_weight = sum(w for _, w ,_ in tasks)
            tasks.sort(key=lambda x: x[2])  # 按元组第3个元素（order）从小到大排序

            print("\n--- 今日计划 ---")
            with open("plan.txt", "w", encoding="utf-8") as f:
                for name, w,_ in tasks:
                    # 计算分配时间
                    time_allocated = hours * w / total_weight
                    result_str = f"{name}: {time_allocated:.1f}小时\n"

                    # 打印到屏幕
                    print(result_str, end="")

                    # 写入文件
                    f.write(result_str)
        else:
            print("未输入任何任务。")

    except ValueError:
        print("输入错误：权重和时长必须是数字！")
    except Exception as e:
        print(f"发生未知错误: {e}")

# 调用函数运行
calculate_plan()


