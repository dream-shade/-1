from collections import deque


def simulate(initial, n=10, max_steps=500):
    """
    正向模拟：
      放下去 = 手牌顶 -> 桌面顶（桌面累积）
      拿出来 = 桌面整叠翻转 -> 放回手牌顶部
    """
    hand = deque(initial)
    table = deque()
    step = 0
    target = list(range(1, n + 1))

    print(f"初始手牌（上→下）：{list(hand)}\n")

    while step < max_steps:
        # ① 放下去：手牌顶 -> 桌面
        if hand:
            card = hand.popleft()
            table.appendleft(card)
            step += 1
            print(f"步骤{step:3d}: 放下去 {card:2d}   手牌:{list(hand)}  桌面:{list(table)}")

        # ② 拿出来：桌面整叠翻转后放回手牌顶部
        if table:
            while table:
                hand.appendleft(table.popleft())   # 整叠翻转放回顶部
            step += 1
            print(f"步骤{step:3d}: 拿出来(整叠)  手牌:{list(hand)}  桌面:{list(table)}")

        if list(hand) == target:
            print(f"\n✅ 排序成功！共 {step} 步，最终手牌：{list(hand)}")
            return True

    print(f"\n❌ 超过 {max_steps} 步仍未排序，当前手牌：{list(hand)}")
    return False


def reverse_solve(n=10):
    """
    逆推求初始牌序：
    从最终有序状态 1..n 出发，反向执行操作
    """
    hand = deque(range(1, n + 1))
    # 逆推 n 轮：每轮反向执行"拿出来"和"放下去"
    for _ in range(n):
        # 逆"拿出来"：手牌顶部若干张回到桌面（这里取整叠逆操作）
        # 逆"放下去"：桌面牌回到手牌顶
        card = hand.pop()          # 从底部取（逆放下去）
        hand.appendleft(card)      # 放回顶部
    return list(hand)


def brute_force(n=10):
    """暴力搜索：找出能让模拟排序成功的初始牌序"""
    from itertools import permutations
    target = list(range(1, n + 1))

    def ok(order):
        hand = deque(order)
        table = deque()
        for _ in range(4 * n):
            if hand:
                table.appendleft(hand.popleft())
            if table:
                while table:
                    hand.appendleft(table.popleft())
            if list(hand) == target:
                return True
        return False

    # 固定第一张为 1 减少搜索量（可根据实际情况调整）
    for perm in permutations(range(1, n + 1)):
        if ok(perm):
            return list(perm)
    return None


if __name__ == "__main__":
    print("=" * 60)
    print("10张扑克牌排序（放下去，拿出来）")
    print("=" * 60)

    # 先验证聊天框里的答案
    print("\n【验证聊天框答案】8 1 6 2 10 3 7 4 9 5")
    print("-" * 60)
    simulate([8, 1, 6, 2, 10, 3, 7, 4, 9, 5])

    # 逆推求答案
    print("\n" + "=" * 60)
    print("【逆推求解】")
    ans = reverse_solve(10)
    print(f"逆推结果：{ans}")
    print("-" * 60)
    simulate(ans)