import random
from datetime import datetime, timedelta

# 基础配置
departments = ['zy', 'js', 'zd', 'yh', 'gl', 'jd', 'jx']  # 学院代码
start_year = 2000  # 入学年份起始
end_year = 2023    # 入学年份结束

def random_name():
    """生成4-8位随机英文名（首字母大写）"""
    chars = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join(random.choices(chars, k=random.randint(4,8))).capitalize()

def random_gender():
    """生成性别（5%概率为NULL）"""
    rand = random.random()
    return '男' if rand < 0.475 else '女' if rand < 0.95 else None

def random_birthdate():
    """生成1980-2000之间的合法日期（MM-DD-YYYY格式）"""
    start = datetime(1980, 1, 1)
    end = datetime(2000, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_date = start + timedelta(days=random_days)
    return random_date.strftime('%m-%d-%Y')  # 确保MM-DD-YYYY格式

with open('tc.txt', 'w', encoding='utf-8') as f:
    for i in range(20000):
        # 生成学号（补零到10位）
        xh = f"{i:010d}"
        
        # 生成数据
        xm = random_name()
        xb = random_gender()
        ydh = random.choice(departments)
        bj = f"0801{random.randint(start_year, end_year)}"
        chrq = random_birthdate()
        
        # 构建SQL（确保NULL值正确）
        sql = (
            f"INSERT INTO xs (xm, xb, xh, ydh, bj, chrq) VALUES ("
            f"'{xm}', "
            f"{f"'{xb}'" if xb is not None else 'NULL'}, "
            f"'{xh}', "
            f"'{ydh}', "
            f"'{bj}', "
            f"'{chrq}'"
            ");\n"
        )
        
        f.write(sql)

print("生成完成，文件已保存到 tc.txt")