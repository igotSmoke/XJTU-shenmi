import tkinter as tk
from tkinter import ttk, messagebox

# 指令对象，表示一条MIPS指令及其状态
class Instruction:
    def __init__(self, op, dst, src1=None, src2=None, imm=None, raw=None):
        self.op = op  # 操作类型，如add.d、load等
        self.dst = dst  # 目的寄存器
        self.src1 = src1  # 源寄存器1
        self.src2 = src2  # 源寄存器2
        self.imm = imm  # 立即数（如load/store偏移）
        self.raw = raw  # 原始指令文本
        self.issue = None  # 发射时钟周期
        self.start_exec = None  # 开始执行时钟周期 
        self.end_exec = None  # 结束执行时钟周期
        self.write_back = None  # 写回时钟周期
        self.status = "等待"  # 当前状态

# 保留站对象，表示一个功能部件的占用情况
class ReservationStation:
    def __init__(self, name, op_type):
        self.name = name  # 保留站名称
        self.op_type = op_type  # 类型（add/mul/load）
        self.busy = False  # 是否被占用
        self.op = None  # 当前操作类型
        self.Vj = None  # 操作数j的值
        self.Vk = None  # 操作数k的值
        self.Qj = None  # 操作数j的来源（等待哪个保留站）
        self.Qk = None  # 操作数k的来源
        self.A = None  # 地址字段（load/store用）
        self.instr = None  # 当前指令对象
        self.remaining = 0  # 剩余执行周期
        self.Qj_ready = False
        self.Qk_ready = False

    def clear(self):
        # 清空保留站状态
        self.busy = False
        self.op = None
        self.Vj = None
        self.Vk = None
        self.Qj = None
        self.Qk = None
        self.A = None
        self.instr = None
        self.remaining = 0

# 执行时间配置对象
class ExecutionConfig:
    def __init__(self, load=2, store=2, add=2, mul=10, div=40):
        self.load = load  # load指令执行周期
        self.store = store  # store指令执行周期
        self.add = add  # add/sub指令执行周期
        self.mul = mul  # mul指令执行周期
        self.div = div  # div指令执行周期

# Tomasulo算法模拟器核心
class TomasuloSimulator:
    def __init__(self, exec_config):
        self.exec_config = exec_config  # 执行时间配置
        self.clock = 0  # 当前时钟周期
        self.instructions = []  # 指令列表 
        self.pc = 0  # 程序计数器，指向下一条待发射指令
        self.finished_instr = 0  # 已完成指令数
        # 初始化保留站
        self.res_stations = [
            ReservationStation('Add1', 'add'),
            ReservationStation('Add2', 'add'),
            ReservationStation('Add3', 'add'),
            ReservationStation('Mul1', 'mul'),
            ReservationStation('Mul2', 'mul'),
            ReservationStation('Load1', 'load'),
            ReservationStation('Load2', 'load'),
            ReservationStation('Load3', 'load'),
        ]
        # F0, F2, ..., F30
        self.reg_status = {f'F{i}': None for i in range(0, 32, 2)}
        self.reg_value = {f'F{i}': 0.0 for i in range(0, 32, 2)}
        # R寄存器，仅用于load/store寻址
        self.R_value = {f'R{i}': 0.0 for i in range(0, 32)}
        # 内存，简化为100个单元，初值1.0
        self.mem = {i: 1.0 for i in range(0, 100)}

    def reset(self):
        # 重置模拟器状态
        self.clock = 0
        self.pc = 0
        self.finished_instr = 0
        for rs in self.res_stations:
            rs.clear()
        for k in self.reg_status:
            self.reg_status[k] = None
        for k in self.reg_value:
            self.reg_value[k] = 0.0
        self.mem = {i: 1.0 for i in range(0, 100)}
        for instr in self.instructions:
            instr.issue = instr.start_exec = instr.end_exec = instr.write_back = None
            instr.status = "等待"

    def load_program(self, program):
        # 加载并解析MIPS程序
        self.instructions = []
        for line in program.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            instr = self.parse_instruction(line)
            if instr:
                self.instructions.append(instr)
        self.reset()

    def parse_instruction(self, line):
        # 解析一条MIPS指令，支持load/store/add.d/sub.d/mul.d/div.d
        tokens = line.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
        if not tokens:
            return None
        op = tokens[0].lower()
        if op == 'load':
            # load F2, 0(R4)
            dst = tokens[1]
            addr_reg = tokens[3]
            if not (dst.startswith('F') and dst[1:].isdigit() and int(dst[1:]) % 2 == 0):
                return None  # 只允许F0, F2, ..., F30
            return Instruction('load', dst, addr_reg, imm=int(tokens[2]), raw=line)
        elif op == 'store':
            # store F2, 0(R4)
            src = tokens[1]
            addr_reg = tokens[3]
            if not (src.startswith('F') and src[1:].isdigit() and int(src[1:]) % 2 == 0):
                return None  # 只允许F0, F2, ..., F30
            return Instruction('store', src, addr_reg, imm=int(tokens[2]), raw=line)
        elif op in ['add.d', 'sub.d', 'mul.d', 'div.d']:
            # add.d F2, F4, F6
            dst, src1, src2 = tokens[1], tokens[2], tokens[3]
            # 检查寄存器编号
            for reg in [dst, src1, src2]:
                if not (reg.startswith('F') and reg[1:].isdigit() and int(reg[1:]) % 2 == 0):
                    return None
            return Instruction(op, dst, src1, src2, raw=line)
        else:
            return None

    def step(self):
        # 执行一个时钟周期
        self.clock += 1
        # 1. 写回阶段
        for rs in self.res_stations:
            if rs.busy and rs.remaining == 0 and rs.instr and rs.instr.write_back is None:
                rs.instr.write_back = self.clock
                rs.instr.status = "写回"
                # 写回寄存器
                result = None
                if rs.op in ['add.d', 'sub.d', 'mul.d', 'div.d', 'load']:
                    if rs.instr.dst:
                        if self.reg_status[rs.instr.dst] == rs.name:
                            self.reg_status[rs.instr.dst] = None
                        result = self.calc_result(rs)
                        self.reg_value[rs.instr.dst] = result
                else:
                    result = self.calc_result(rs)
                # Tomasulo结果广播，更新所有保留站的Qj/Qk
                for other_rs in self.res_stations:
                    if other_rs.busy:
                        if other_rs.Qj == rs.name:
                            other_rs.Vj = result
                            other_rs.Qj = None
                        if other_rs.Qk == rs.name:
                            other_rs.Vk = result
                            other_rs.Qk = None
                rs.clear()
                self.finished_instr += 1
        # 2. 执行阶段
        for rs in self.res_stations:
            if rs.busy and rs.remaining > 0:
                # 操作数已就绪
                if rs.Qj_ready and rs.Qk_ready:
                    if rs.instr.start_exec is None:
                        rs.instr.start_exec = self.clock
                        rs.instr.status = "执行"
                    rs.remaining -= 1
                    if rs.remaining == 0:
                        rs.instr.end_exec = self.clock
        # 3. 发射阶段
        if self.pc < len(self.instructions):
            instr = self.instructions[self.pc]
            rs = self.find_free_rs(instr.op)
            if rs:
                rs.busy = True
                rs.op = instr.op
                rs.instr = instr
                if instr.op == 'load':
                    # 计算地址，R寄存器寻址
                    rs.A = instr.imm + self.R_value.get(instr.src1, 0.0)
                    rs.remaining = self.exec_config.load
                    if self.reg_status[instr.dst] is None:
                        rs.Vj = None
                        rs.Qj = None
                    else:
                        rs.Qj = self.reg_status[instr.dst]
                    self.reg_status[instr.dst] = rs.name
                elif instr.op == 'store':
                    # 计算地址，R寄存器寻址，Vj为F寄存器的值
                    rs.A = instr.imm + self.R_value.get(instr.src2, 0.0)
                    rs.Vj = self.reg_value.get(instr.src1, 0.0)
                    rs.remaining = self.exec_config.store
                elif instr.op in ['add.d', 'sub.d']:
                    rs.remaining = self.exec_config.add
                    # 检查源操作数是否就绪
                    for i, reg in enumerate([instr.src1, instr.src2]):
                        if self.reg_status[reg] is None:
                            if i == 0:
                                rs.Vj = self.reg_value[reg]
                                rs.Qj = None
                            else:
                                rs.Vk = self.reg_value[reg]
                                rs.Qk = None
                        else:
                            if i == 0:
                                rs.Qj = self.reg_status[reg]
                            else:
                                rs.Qk = self.reg_status[reg]
                    self.reg_status[instr.dst] = rs.name
                elif instr.op == 'mul.d':
                    rs.remaining = self.exec_config.mul
                    for i, reg in enumerate([instr.src1, instr.src2]):
                        if self.reg_status[reg] is None:
                            if i == 0:
                                rs.Vj = self.reg_value[reg]
                                rs.Qj = None
                            else:
                                rs.Vk = self.reg_value[reg]
                                rs.Qk = None
                        else:
                            if i == 0:
                                rs.Qj = self.reg_status[reg]
                            else:
                                rs.Qk = self.reg_status[reg]
                    self.reg_status[instr.dst] = rs.name
                elif instr.op == 'div.d':
                    rs.remaining = self.exec_config.div
                    for i, reg in enumerate([instr.src1, instr.src2]):
                        if self.reg_status[reg] is None:
                            if i == 0:
                                rs.Vj = self.reg_value[reg]
                                rs.Qj = None
                            else:
                                rs.Vk = self.reg_value[reg]
                                rs.Qk = None
                        else:
                            if i == 0:
                                rs.Qj = self.reg_status[reg]
                            else:
                                rs.Qk = self.reg_status[reg]
                    self.reg_status[instr.dst] = rs.name
                instr.issue = self.clock
                instr.status = "发射"
                self.pc += 1
        for rs in self.res_stations:
            if rs.Qj is None:
                rs.Qj_ready = True
            else:
                rs.Qj_ready = False
            if rs.Qk is None:
                rs.Qk_ready = True
            else:
                rs.Qk_ready = False

    def step_n(self, n):
        # 连续执行n个时钟周期
        for _ in range(n):
            if self.finished_instr >= len(self.instructions):
                break
            self.step()

    def run_all(self):
        # 一直执行到所有指令完成
        while self.finished_instr < len(self.instructions):
            self.step()

    def find_free_rs(self, op):
        # 查找空闲的保留站
        if op in ['add.d', 'sub.d']:
            for rs in self.res_stations:
                if rs.op_type == 'add' and not rs.busy:
                    return rs
        elif op in ['mul.d', 'div.d']:
            for rs in self.res_stations:
                if rs.op_type == 'mul' and not rs.busy:
                    return rs
        elif op == 'load':
            for rs in self.res_stations:
                if rs.op_type == 'load' and not rs.busy:
                    return rs
        elif op == 'store':
            for rs in self.res_stations:
                if rs.op_type == 'load' and not rs.busy:
                    return rs
        return None

    def calc_result(self, rs):
        # 计算指令结果
        if rs.op == 'add.d':
            return rs.Vj + rs.Vk
        elif rs.op == 'sub.d':
            return rs.Vj - rs.Vk
        elif rs.op == 'mul.d':
            return rs.Vj * rs.Vk
        elif rs.op == 'div.d':
            return rs.Vj / rs.Vk if rs.Vk != 0 else 0.0
        elif rs.op == 'load':
            return self.mem.get(int(rs.A), 0.0)
        return 0.0

    def finished(self):
        # 判断是否所有指令都已完成
        return self.finished_instr >= len(self.instructions)

    def get_status(self):
        # 生成状态表字符串，包含指令状态、保留站状态、寄存器状态
        s = f"时钟周期: {self.clock}\n\n[指令状态表]\n"
        s += f"{'指令':<30}{'发射':<6}{'开始执行':<8}{'结束执行':<8}{'写回':<6}{'状态':<6}\n"
        for instr in self.instructions:
            s += f"{instr.raw:<30}{str(instr.issue):<6}{str(instr.start_exec):<8}{str(instr.end_exec):<8}{str(instr.write_back):<6}{instr.status:<6}\n"
        # 保留站状态表
        s += "\n[保留站状态表]\n"
        s += f"{'名称':<6}{'Busy':<6}{'Op':<8}{'Vj':<8}{'Vk':<8}{'Qj':<8}{'Qk':<8}{'A':<8}{'剩余':<6}\n"
        for rs in self.res_stations:
            s += f"{rs.name:<6}{str(rs.busy):<6}{str(rs.op):<8}{str(rs.Vj):<8}{str(rs.Vk):<8}{str(rs.Qj):<8}{str(rs.Qk):<8}{str(rs.A):<8}{str(rs.remaining):<6}\n"
        # 寄存器状态表
        s += "\n[寄存器状态表]\n"
        s += f"{'寄存器':<8}{'Qi':<8}{'值':<8}\n"
        for k in sorted(self.reg_status.keys(), key=lambda x: int(x[1:])):
            s += f"{k:<8}{str(self.reg_status[k]):<8}{str(self.reg_value[k]):<8}\n"
        return s

    def get_cpi(self):
        if len(self.instructions) == 0:
            return 0.0
        return self.clock / len(self.instructions)

# 图形界面类，负责tkinter窗口和交互
class TomasuloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tomasulo模拟器")
        self.exec_config = ExecutionConfig()  # 执行时间配置
        self.sim = TomasuloSimulator(self.exec_config)  # 模拟器实例
        self.create_widgets()  # 创建界面控件

    def create_widgets(self):
        # 程序输入区
        frame1 = tk.Frame(self.root)
        frame1.pack(fill=tk.X)
        tk.Label(frame1, text="输入MIPS程序:").pack(side=tk.LEFT)
        self.program_text = tk.Text(frame1, height=8, width=60)
        self.program_text.pack(side=tk.LEFT)
        # 执行时间调整区
        frame2 = tk.Frame(self.root)
        frame2.pack(fill=tk.X)
        tk.Label(frame2, text="Load/Store时间:").pack(side=tk.LEFT)
        self.load_time = tk.IntVar(value=2)
        tk.Entry(frame2, textvariable=self.load_time, width=3).pack(side=tk.LEFT)
        tk.Label(frame2, text="Mul时间:").pack(side=tk.LEFT)
        self.mul_time = tk.IntVar(value=10)
        tk.Entry(frame2, textvariable=self.mul_time, width=3).pack(side=tk.LEFT)
        tk.Label(frame2, text="Div时间:").pack(side=tk.LEFT)
        self.div_time = tk.IntVar(value=40)
        tk.Entry(frame2, textvariable=self.div_time, width=3).pack(side=tk.LEFT)
        tk.Label(frame2, text="Add/Sub时间:").pack(side=tk.LEFT)
        self.add_time = tk.IntVar(value=2)
        tk.Entry(frame2, textvariable=self.add_time, width=3).pack(side=tk.LEFT)
        # 控制按钮区
        frame3 = tk.Frame(self.root)
        frame3.pack(fill=tk.X)
        tk.Button(frame3, text="加载程序", command=self.load_program).pack(side=tk.LEFT)
        tk.Button(frame3, text="单步执行", command=self.step).pack(side=tk.LEFT)
        tk.Button(frame3, text="执行5步", command=self.step5).pack(side=tk.LEFT)
        tk.Button(frame3, text="全部执行", command=self.run_all).pack(side=tk.LEFT)
        tk.Button(frame3, text="重置", command=self.reset).pack(side=tk.LEFT)
        # 状态表显示区
        frame4 = tk.Frame(self.root)
        frame4.pack(fill=tk.BOTH, expand=True)
        self.status_table = tk.Text(frame4, height=30, width=100)
        self.status_table.pack(fill=tk.BOTH, expand=True)

    def load_program(self):
        # 加载用户输入的MIPS程序
        program = self.program_text.get(1.0, tk.END)
        # 设置执行时间参数
        self.exec_config.load = self.load_time.get()
        self.exec_config.store = self.load_time.get()
        self.exec_config.mul = self.mul_time.get()
        self.exec_config.div = self.div_time.get()
        self.exec_config.add = self.add_time.get()
        self.sim.load_program(program)
        self.update_status()

    def step(self):
        # 单步执行
        if self.sim.finished():
            messagebox.showinfo("提示", "程序已执行完毕！\nCPI: %.2f" % self.sim.get_cpi())
            return
        self.sim.step()
        self.update_status()
        if self.sim.finished():
            messagebox.showinfo("提示", "程序已执行完毕！\nCPI: %.2f" % self.sim.get_cpi())

    def step5(self):
        # 连续执行5步
        if self.sim.finished():
            messagebox.showinfo("提示", "程序已执行完毕！\nCPI: %.2f" % self.sim.get_cpi())
            return
        self.sim.step_n(5)
        self.update_status()
        if self.sim.finished():
            messagebox.showinfo("提示", "程序已执行完毕！\nCPI: %.2f" % self.sim.get_cpi())

    def run_all(self):
        # 一直执行到结束
        if self.sim.finished():
            messagebox.showinfo("提示", "程序已执行完毕！\nCPI: %.2f" % self.sim.get_cpi())
            return
        self.sim.run_all()
        self.update_status()
        if self.sim.finished():
            messagebox.showinfo("提示", "程序已执行完毕！\nCPI: %.2f" % self.sim.get_cpi())

    def reset(self):
        # 重置模拟器
        self.sim.reset()
        self.update_status()

    def update_status(self):
        # 刷新状态表显示
        self.status_table.delete(1.0, tk.END)
        self.status_table.insert(tk.END, self.sim.get_status())

if __name__ == '__main__':
    # 启动主窗口
    root = tk.Tk()
    app = TomasuloGUI(root)
    root.mainloop()
