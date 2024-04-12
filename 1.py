from collections import Counter


class MyObject:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    # 创建对象列表


objects = [
    MyObject('A', 10),
    MyObject('B', 5),
    MyObject('C', 10),
    MyObject('D', 5),
    MyObject('E', 20),
]

# 提取每个对象的value属性并计数  
value_counts = Counter(obj.value for obj in objects)

# 打印结果  
for value, count in value_counts.items():
    print(f"Value {value} appears {count} times.")