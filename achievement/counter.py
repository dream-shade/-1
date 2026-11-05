def analyze_word(word):

    from collections import Counter # 导入计数器

  
    my_counter = Counter(word) # 一行代码，直接帮你统计完！

    print(my_counter)
    max_count=max(my_counter.values())
    candidates=[letter for letter,count in my_counter.items()if count==max_count]
    result_letter=min(candidates)
    print(f"出现最多的字母是{result_letter},次数是{max_count}")
    return result_letter, max_count
if __name__=="__main__":
    word=input("输入")
    letter,count=analyze_word(word)
    print(f"{letter}{count}")

'''word = input("输入单词")
my_dict = {}
for letter in word:
    if letter in my_dict:
        my_dict[letter] += 1 # 抽屉里已经有数字了，加1
    else:
        my_dict[letter] = 1  # 第一次见，建个抽屉放1

print(my_dict) 
# 结果：{'a': 1, 'p': 2, 'l': 1, 'e': 1}
'''