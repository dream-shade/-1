def binary_search(arr: list[int], target: int) -> int:
    """
    在有序数组 arr 中查找目标值 target。
    如果找到，返回索引；否则返回 -1。
    """
    
    # 【第2步：异常处理】放在函数第一行，先拦截！
    if not arr:
        print("传个空列表给我干嘛？")
        return -1 
    
    # 核心二分查找逻辑
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2  # 计算中间索引

        if arr[mid] == target:
            return mid  # 找到了，返回索引
        elif arr[mid] < target:
            left = mid + 1  # 目标在右边，左指针右移
        else:
            right = mid - 1  # 目标在左边，右指针左移

    return -1  # 循环结束未找到，返回 -


# 【第3步：写测试】直接运行，看能不能跑通
assert binary_search([1, 2, 3], 2) == 1, "测试失败：找不到元素"
print("恭喜你！二分查找代码升级成功，全部测试通过！")