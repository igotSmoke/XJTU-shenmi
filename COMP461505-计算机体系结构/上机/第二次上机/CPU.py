import tkinter as tk  # 导入tkinter库，用于GUI界面
from tkinter import ttk, messagebox, scrolledtext  # 导入tkinter的子模块

REG_NAMES = [f"${i}" for i in range(32)]  # 32个寄存器的名字列表

class Instruction:
    def __init__(self, text, idx):
        self.text = text.strip()  # 指令文本内容
        self.idx = idx  # 指令在程序中的索引
        self.stage_history = []  # 记录每周期所处阶段
        self.parse()  # 解析指令
        self.finished = False  # 指令是否已完成
        self.entered_if = False  # 是否已进入IF阶段

    def parse(self):
        if self.text.endswith(':'):
            self.is_label = True
            self.op = "label"   # 标签
            self.args = []  
        else:
            self.is_label = False
            parts = self.text.replace(',', '').split()  # 按空格分割，去掉逗号
            self.op = parts[0]  # 操作码
            self.args = parts[1:]  # 操作数参数

class RegisterFile:
    def __init__(self):
        self.regs = [0] * 32  # 32个寄存器，初始值为0

    def __getitem__(self, reg):
        idx = int(reg.replace('$', ''))  # 获取寄存器编号
        return self.regs[idx]  # 返回寄存器值

    def __setitem__(self, reg, value):
        idx = int(reg.replace('$', ''))  # 获取寄存器编号
        self.regs[idx] = value  # 设置寄存器值

class Memory:
    def __init__(self):
        self.mem = {}  # 内存用字典表示，地址为key，值为value

    def __getitem__(self, addr):
        return self.mem.get(addr, 0)  # 读取内存，默认值为0

    def __setitem__(self, addr, value):
        self.mem[addr] = value  # 写内存

class Pipeline:
    def __init__(self, regfile, memory, use_forwarding):
        self.regfile = regfile  # 寄存器文件对象
        self.memory = memory  # 内存对象
        self.use_forwarding = use_forwarding  # 是否启用数据前递
        self.instructions = []  # 指令列表
        self.pc = 0  # 程序计数器
        self.cycle = 0  # 当前周期数
        self.finished = False  # 是否执行完毕
        self.stages = [None] * 5  # 五个流水线阶段：[IF, ID, EX, MEM, WB]
        self.in_pipeline = []     # 只记录已进流水线的指令
        self.branch_pending = False  # 是否有分支待处理
        self.branch_target = None  # 分支目标指令索引
        self.stall = 0  # 暂停周期数（未实际使用）

    def load_program(self, instructions):
        self.instructions = instructions  # 加载指令
        self.pc = 0  # 重置PC
        self.cycle = 0  # 重置周期
        self.finished = False  # 重置完成标志
        self.stages = [None] * 5  # 清空流水线
        self.in_pipeline = []  # 清空流水线指令
        self.branch_pending = False  # 清空分支标志
        self.branch_target = None  # 清空分支目标
        self.stall = 0  # 清空暂停
        for inst in self.instructions:
            inst.stage_history = []  # 清空每条指令的阶段历史
            inst.finished = False  # 重置完成标志
            inst.entered_if = False  # 重置IF标志

    def step(self):
    

        if self.finished:
            return

        # 检查ID段RAW冒险
        stall_needed = False  # 是否需要暂停
        if not self.use_forwarding and self.stages[1]:
            id_inst = self.stages[1]  # 当前ID段指令
            id_srcs = []  # ID段源操作数
            if id_inst.op == "add":
                id_srcs = [id_inst.args[1], id_inst.args[2]]  # add的两个源寄存器
            elif id_inst.op == "lw":
                id_srcs = [id_inst.args[1].split('(')[1][:-1]]  # lw的源寄存器
            elif id_inst.op == "sw":
                id_srcs = [id_inst.args[0], id_inst.args[1].split('(')[1][:-1]]  # sw的源寄存器
            elif id_inst.op == "beqz":
                id_srcs = [id_inst.args[0]]  # beqz的源寄存器
            for stage_idx in [2, 3, 4]:  # EX, MEM, WB
                inst = self.stages[stage_idx]  # 检查流水线后段指令
                if inst and inst.op in ("add", "lw"):
                    dest = inst.args[0]  # 目的寄存器
                    if dest in id_srcs:
                        if stage_idx != 4:
                            stall_needed = True  # 检测到冒险需暂停
                            break
        
        forwarding_stall_needed = False
        if self.use_forwarding and self.stages[1]:
            ex_inst = self.stages[1]
            ex_srcs = []
            if ex_inst.op == "add":
                ex_srcs = [ex_inst.args[1], ex_inst.args[2]]  # add的两个源寄存器
            elif ex_inst.op == "lw":
                ex_srcs = [ex_inst.args[1].split('(')[1][:-1]]  # lw的源寄存器
            elif ex_inst.op == "sw":
                ex_srcs = [ex_inst.args[0], ex_inst.args[1].split('(')[1][:-1]]  # sw的源寄存器
            elif ex_inst.op == "beqz":
                ex_srcs = [ex_inst.args[0]]  # beqz的源寄存器
            inst = self.stages[2]
            if inst and inst.op == "lw":
                dest = inst.args[0]
                if dest in ex_srcs:
                    forwarding_stall_needed = True

        beqz_IF_pause = False        
        if self.stages[0] and self.stages[0].op == "beqz": 
            beqz_IF_pause = True

                        
        # 检查分支冒险（beqz在EX段判断）
        if self.stages[1] and self.stages[1].op == "beqz":
            rs, label = self.stages[1].args  # beqz的源寄存器和目标标签
            if self.regfile[rs] == 0:
                for i, ins in enumerate(self.instructions):
                    if ins.text.startswith(label + ":"):
                        self.branch_pending = True  # 标记分支待处理
                        self.branch_target = i+1 # 记录分支目标
                        break
            else:
                self.branch_pending = False  # 不跳转

        # 推进流水线（后段先推进）
        self.stages[4] = self.stages[3]  # MEM->WB
        self.stages[3] = self.stages[2]  # EX->MEM

        if self.use_forwarding and self.stages[1]:
            if forwarding_stall_needed:
                self.stages[1].stage_history.append('ID')
            else:
                if self.stages[1].stage_history[-1] == 'ID':
                    self.stages[1].stage_history.append('stall')
                else:
                    self.stages[1].stage_history.append('ID')

        # 定向技术处理ID/EX推进和写入
        if forwarding_stall_needed:
            self.stages[2] = None
            
            if self.stages[0] and self.stages[0].entered_if:
                self.stages[0].stage_history.append('stall')
        # 非定向技术处理ID/EX推进和写入
        elif stall_needed:

            # EX段不推进，ID段写入stall
            self.stages[2] = None
            if self.stages[1]:
                self.stages[1].stage_history.append('stall')  # 记录暂停
            # IF段不推进，已进入IF的指令补stall
            if self.stages[0] and self.stages[0].entered_if:
                self.stages[0].stage_history.append('stall')
        else:

            # EX段推进
            self.stages[2] = self.stages[1]
            # ID段推进，写入ID
            if self.stages[1] and not self.use_forwarding:
                self.stages[1].stage_history.append('ID')  # 记录ID阶段
            self.stages[1] = self.stages[0]
            # IF段推进
            if self.branch_pending:
                if self.branch_target is not None:
                    inst = self.instructions[self.branch_target]  # 分支目标指令
                    while len(inst.stage_history) < self.cycle:
                        inst.stage_history.append("")  # 补齐历史
                    if not inst.entered_if:
                        inst.stage_history.append('IF')  # 记录IF阶段
                        inst.entered_if = True
                        self.in_pipeline.append(inst)  # 加入流水线
                    self.stages[0] = inst  # IF段为分支目标
                    self.pc = self.branch_target + 1  # PC跳转
                else:
                    self.stages[0] = None
                self.branch_pending = False  # 清空分支标志
                self.branch_target = None
            else:
                if self.pc < len(self.instructions) and not beqz_IF_pause:
                                  
                    inst = self.instructions[self.pc]  # 取下一条指令
                    while inst.is_label:
                        self.pc += 1
                        inst = self.instructions[self.pc]
                    while len(inst.stage_history) < self.cycle:
                        inst.stage_history.append("")
                    if not inst.entered_if:
                        inst.stage_history.append('IF')
                        inst.entered_if = True
                        self.in_pipeline.append(inst)
                    self.stages[0] = inst
                    self.pc += 1  # PC递增
                else:
                    self.stages[0] = None

        # 其它流水线阶段推进和写入
        # EX段
        if self.stages[2]:
            self.stages[2].stage_history.append('EX')  # 记录EX阶段
        # MEM段
        if self.stages[3]:
            self.stages[3].stage_history.append('MEM')  # 记录MEM阶段
        # WB段
        if self.stages[4] and not self.stages[4].finished:
            self.stages[4].stage_history.append('WB')  # 记录WB阶段
            self.write_back(self.stages[4])  # 写回
            self.stages[4].finished = True  # 标记完成

        # MEM/EX段操作
        if self.stages[3]:
            self.memory_access(self.stages[3])  # 访存
        if self.stages[2]:
            self.execute(self.stages[2])  # 执行

        self.cycle += 1  # 周期加一

        # 检查是否全部完成
        if all(x is None or getattr(x, 'finished', False) for x in self.stages) and self.pc > len(self.instructions):
            self.finished = True
        if all(x is None or getattr(x, 'finished', False) for x in self.stages) and self.pc >= len(self.instructions):
            self.pc += 1
        

    def execute(self, inst):
        # 执行阶段：计算结果或地址
        if inst.op == "add":
            rd, rs, rt = inst.args  # 目的寄存器、两个源寄存器
            inst.result = self.regfile[rs] + self.regfile[rt]  # 计算加法
        elif inst.op == "lw":
            rt, offset_rs = inst.args  # 目标寄存器，偏移量和基址
            offset, rs = offset_rs.replace(')', '').split('(')
            addr = self.regfile[rs] + int(offset)  # 计算内存地址
            inst.mem_addr = addr  # 保存地址
        elif inst.op == "sw":
            rt, offset_rs = inst.args  # 源寄存器，偏移量和基址
            offset, rs = offset_rs.replace(')', '').split('(')
            addr = self.regfile[rs] + int(offset)
            inst.mem_addr = addr
        # beqz在step里处理分支冒险

    def memory_access(self, inst):
        # 访存阶段
        if inst.op == "lw":
            inst.result = self.memory[inst.mem_addr]  # 读取内存
        elif inst.op == "sw":
            self.memory[inst.mem_addr] = self.regfile[inst.args[0]]  # 写内存

    def write_back(self, inst):
        # 写回阶段
        if inst.op == "add":
            self.regfile[inst.args[0]] = inst.result  # 写回寄存器
        elif inst.op == "lw":
            self.regfile[inst.args[0]] = inst.result  # 写回寄存器

class PipelineGUI:
    def __init__(self, root):

        self.root = root  # 主窗口
        self.root.title("MIPS五段流水线模拟器")  # 窗口标题
        
        self.instructions = []  # 指令列表
        self.regfile = RegisterFile()  # 寄存器文件
        self.memory = Memory()  # 内存
        self.pipeline = Pipeline(self.regfile, self.memory, use_forwarding=False)  # 流水线对象

        self.code_input = scrolledtext.ScrolledText(root, width=40, height=10)  # 代码输入框
        self.code_input.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        self.load_btn = tk.Button(root, text="加载程序", command=self.load_program)  # 加载按钮
        self.load_btn.grid(row=1, column=0)
        self.step_btn = tk.Button(root, text="单步执行", command=self.step)  # 单步执行按钮
        self.step_btn.grid(row=1, column=1)
        self.run_btn = tk.Button(root, text="运行到结束", command=self.run_to_end)  # 运行到结束按钮
        self.run_btn.grid(row=1, column=2)
        self.forward_var = tk.BooleanVar()  # 是否启用前递的变量
        self.forward_check = tk.Checkbutton(root, text="定向(数据前递)", variable=self.forward_var, command=self.toggle_forwarding)  # 前递勾选框
        self.forward_check.grid(row=1, column=3)

        self.pipeline_table = ttk.Treeview(root, columns=[], show="headings", height=10)
        self.pipeline_table.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # 新增：横向滚动条
        self.pipeline_xscroll = ttk.Scrollbar(root, orient="horizontal", command=self.pipeline_table.xview)
        self.pipeline_table.configure(xscrollcommand=self.pipeline_xscroll.set)
        self.pipeline_xscroll.grid(row=3, column=0, columnspan=4, sticky="ew")

        # 让主窗口支持自动拉伸
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)

        self.reg_table = ttk.Treeview(root, columns=["寄存器", "值"], show="headings", height=8)  # 寄存器显示表格
        self.reg_table.heading("寄存器", text="寄存器")
        self.reg_table.heading("值", text="值")
        self.reg_table.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.status_label = tk.Label(root, text="状态：等待加载程序")  # 状态标签
        self.status_label.grid(row=5, column=0, columnspan=4)

        self.update_reg_table()  # 初始化寄存器表

    def load_program(self):
        code = self.code_input.get("1.0", tk.END).strip().split('\n')  # 获取输入的代码
        self.instructions = [Instruction(line, idx) for idx, line in enumerate(code) if line.strip()]  # 生成指令对象
        self.regfile = RegisterFile()  # 重置寄存器
        self.memory = Memory()  # 重置内存
        self.pipeline = Pipeline(self.regfile, self.memory, self.forward_var.get())  # 新建流水线
        self.pipeline.load_program(self.instructions)  # 加载指令
        self.status_label.config(text="状态：已加载，等待执行")  # 更新状态
        self.update_pipeline_table()  # 刷新流水线表
        self.update_reg_table()  # 刷新寄存器表

    def step(self):
        if not self.pipeline or not self.instructions:
            messagebox.showwarning("警告", "请先加载程序")  # 未加载程序警告
            return
        if self.pipeline.finished:
            self.status_label.config(text="状态：程序已结束")  # 程序结束
            return
        self.pipeline.step()  # 执行一步
        self.update_pipeline_table()  # 刷新流水线表
        self.update_reg_table()  # 刷新寄存器表
        self.status_label.config(text=f"状态：已执行{self.pipeline.cycle}周期")  # 更新状态

    def run_to_end(self):
        if not self.pipeline or not self.instructions:
            messagebox.showwarning("警告", "请先加载程序")  # 未加载程序警告
            return
        while not self.pipeline.finished:
            self.pipeline.step()  # 一直执行到结束
        self.update_pipeline_table()  # 刷新流水线表
        self.update_reg_table()  # 刷新寄存器表
        self.status_label.config(text=f"状态：程序已结束，共{self.pipeline.cycle}周期")  # 更新状态

    def update_pipeline_table(self):
        self.pipeline_table.delete(*self.pipeline_table.get_children())  # 清空表格
        in_pipeline = self.pipeline.in_pipeline if self.pipeline else []  # 当前流水线中的指令
        if not in_pipeline:
            return
        # 只显示到 self.pipeline.cycle-1 列
        max_cycle = max((len(inst.stage_history) for inst in in_pipeline), default=0)  # 最大周期数
        show_cycle = max(0, self.pipeline.cycle - 1)  # 当前显示周期数
        columns = ["指令"] + [f"C{c+1}" for c in range(show_cycle)]  # 列名
        self.pipeline_table["columns"] = columns
        for idx, col in enumerate(columns):
            self.pipeline_table.heading(col, text=col)
            if idx == 0:
                # 第一列"指令"宽度设为200像素
                self.pipeline_table.column(col, width=200, minwidth=200, stretch=False)
            else:
                # 其它列宽度设为40像素
                self.pipeline_table.column(col, width=40, minwidth=40, stretch=False)
        for inst in in_pipeline:
            row = [inst.text] + inst.stage_history[:show_cycle] + [""] * (show_cycle - len(inst.stage_history))  # 每行内容
            self.pipeline_table.insert("", "end", values=row)

    def update_reg_table(self):
        self.reg_table.delete(*self.reg_table.get_children())  # 清空寄存器表
        for i in range(32):
            self.reg_table.insert("", "end", values=(f"${i}", self.regfile.regs[i]))  # 插入寄存器值

    def toggle_forwarding(self):
        if self.pipeline:
            self.pipeline.use_forwarding = self.forward_var.get()  # 切换前递模式

if __name__ == "__main__":
    root = tk.Tk()  # 创建主窗口
    app = PipelineGUI(root)  # 创建GUI应用
    root.mainloop()  # 进入主循环