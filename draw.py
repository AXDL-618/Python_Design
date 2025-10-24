import tkinter as tk
from tkinter import colorchooser, simpledialog, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageGrab
import os
import tempfile


class DrawBoard:
    def __init__(self, app, x, y):
        self.app = app
        self.x = x
        self.y = y
        self.yesno = tk.IntVar(value=0)
        self.what = tk.IntVar(value=1)
        self.X = tk.IntVar(value=0)
        self.Y = tk.IntVar(value=0)
        self.foreColor = '#000000'
        self.backColor = '#FFFFFF'
        self.erase_size = 20
        self.lastDraw = 0
        self.end = [0]
        self.text = ""
        self.image = None
        self.erase_cursor = None
        self.size = 5  # 画笔大小初始值
        self.draw_operations = []

        self.frame = tk.Frame(self.app)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.hscroll = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.hscroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.vscroll = tk.Scrollbar(self.frame)
        self.vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(self.frame, bg='white', width=self.x, height=self.y,
                                xscrollcommand=self.hscroll.set,
                                yscrollcommand=self.vscroll.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.hscroll.config(command=self.canvas.xview)
        self.vscroll.config(command=self.canvas.yview)
        self.canvas.config(scrollregion=(0, 0, self.x, self.y))  # 初始滚动区域
        self.messagebox = tk.messagebox
        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self.onLeftButtonDown)
        self.canvas.bind('<B1-Motion>', self.onLeftButtonMove)
        self.canvas.bind('<ButtonRelease-1>', self.onLeftButtonUp)
        self.canvas.bind('<ButtonRelease-3>', self.onRightButtonUp)
        self.canvas.bind('<Motion>', self.onMouseMove)  # 处理鼠标移动事件

        self.temp_canvas_path = os.path.join(tempfile.gettempdir(), "canvas_temp.png")  # 画布临时保存路径
        self.temp_pil_path = os.path.join(tempfile.gettempdir(), "canvas_pil_temp.png")  # PIL重绘临时保存路径

    def update_erase_cursor(self, x, y):
        """更新橡皮擦光标显示"""
        # 如果坐标超出画布范围，不更新光标
        if x < 0 or y < 0 or x > self.canvas.winfo_width() or y > self.canvas.winfo_height():
            return
            
        if self.erase_cursor:
            self.canvas.delete(self.erase_cursor)

        # 根据鼠标坐标创建橡皮擦光标并添加特殊标签
        self.erase_cursor = self.canvas.create_oval(
            x - self.erase_size // 2,
            y - self.erase_size // 2,
            x + self.erase_size // 2,
            y + self.erase_size // 2,
            outline='#888888',
            dash=(2, 2),
            width=1,
            fill='#CCCCCC',
            stipple='gray25',
            tags=('_erase_cursor_')
        )
        # 将光标置于所有其他对象之上
        self.canvas.tag_raise('_erase_cursor_')

    def onMouseMove(self, event):
        """处理鼠标移动事件，更新橡皮擦光标位置"""
        if self.what.get() == 5:  # 仅在使用橡皮擦工具时更新光标
            self.update_erase_cursor(event.x, event.y)

    def onLeftButtonMove(self, event):
        """鼠标左键移动事件"""
        if self.yesno.get() == 0:
            return

        if self.what.get() == 1:  # 铅笔工具
            # 记录铅笔绘制操作
            self.draw_operations.append({
                'type': 'pencil',
                'x': event.x,
                'y': event.y,
                'size': self.size,
                'fill': self.foreColor
            })

            self.lastDraw = self.canvas.create_oval(
                event.x - self.size // 2,
                event.y - self.size // 2,
                event.x + self.size // 2,
                event.y + self.size // 2,
                fill=self.foreColor,
                outline=self.foreColor)

            if self.X.get() != event.x or self.Y.get() != event.y:
                dx = event.x - self.X.get()
                dy = event.y - self.Y.get()
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance > self.size / 3:
                    steps = int(distance // (self.size / 2)) + 1
                    for i in range(1, steps):
                        ratio = i / steps
                        x = self.X.get() + dx * ratio
                        y = self.Y.get() + dy * ratio

                        # 记录铅笔连续绘制操作
                        self.draw_operations.append({
                            'type': 'pencil',
                            'x': x,
                            'y': y,
                            'size': self.size,
                            'fill': self.foreColor
                        })

                        self.canvas.create_oval(
                            x - self.size // 2,
                            y - self.size // 2,
                            x + self.size // 2,
                            y + self.size // 2,
                            fill=self.foreColor,
                            outline=self.foreColor)

            self.X.set(event.x)
            self.Y.set(event.y)

        elif self.what.get() == 2:  # 直线工具
            try:
                self.canvas.delete(self.lastDraw)
            except:
                pass
            self.lastDraw = self.canvas.create_line(self.X.get(), self.Y.get(), event.x, event.y,
                                                    fill=self.foreColor, width=self.size)

        elif self.what.get() == 3:  # 矩形工具
            try:
                self.canvas.delete(self.lastDraw)
            except:
                pass
            self.lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y,
                                                         outline=self.foreColor, width=self.size)

        elif self.what.get() == 5:  # 橡皮擦工具
            # 记录橡皮擦操作
            self.draw_operations.append({
                'type': 'erase',
                'x': event.x,
                'y': event.y,
                'size': self.erase_size,
                'fill': self.backColor
            })

            # 执行擦除操作
            self.lastDraw = self.canvas.create_oval(
                event.x - self.erase_size // 2,
                event.y - self.erase_size // 2,
                event.x + self.erase_size // 2,
                event.y + self.erase_size // 2,
                fill=self.backColor,
                outline=self.backColor)
            
            # 在鼠标按下移动时更新光标位置
            self.update_erase_cursor(event.x, event.y)

        elif self.what.get() == 6:  # 圆形工具
            try:
                self.canvas.delete(self.lastDraw)
            except:
                pass
            self.lastDraw = self.canvas.create_oval(self.X.get(), self.Y.get(), event.x, event.y,
                                                    outline=self.foreColor, width=self.size)

    def onLeftButtonDown(self, event):
        """鼠标左键按下事件"""
        self.yesno.set(1)
        self.X.set(event.x)
        self.Y.set(event.y)

        # 记录文本绘制操作
        if self.what.get() == 4:
            self.draw_operations.append({
                'type': 'text',
                'x': event.x,
                'y': event.y,
                'text': self.text,
                'font': ("等线", int(self.size)),
                'fill': self.foreColor
            })
            self.canvas.create_text(event.x, event.y,
                                  font=("等线", int(self.size)),
                                  text=self.text,
                                  fill=self.foreColor)
            self.what.set(1)

    def onLeftButtonUp(self, event):
        """鼠标左键释放事件"""
        if self.what.get() == 2:  # 直线
            self.draw_operations.append({
                'type': 'line',
                'x1': self.X.get(),
                'y1': self.Y.get(),
                'x2': event.x,
                'y2': event.y,
                'fill': self.foreColor,
                'width': self.size
            })
            self.lastDraw = self.canvas.create_line(self.X.get(), self.Y.get(), event.x, event.y,
                                                    fill=self.foreColor, width=self.size)

        elif self.what.get() == 3:  # 矩形
            self.draw_operations.append({
                'type': 'rectangle',
                'x1': self.X.get(),
                'y1': self.Y.get(),
                'x2': event.x,
                'y2': event.y,
                'outline': self.foreColor,
                'width': self.size
            })
            self.lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y,
                                                         outline=self.foreColor, width=self.size)

        elif self.what.get() == 6:  # 圆形
            self.draw_operations.append({
                'type': 'oval',
                'x1': self.X.get(),
                'y1': self.Y.get(),
                'x2': event.x,
                'y2': event.y,
                'outline': self.foreColor,
                'width': self.size
            })
            self.lastDraw = self.canvas.create_oval(self.X.get(), self.Y.get(), event.x, event.y,
                                                    outline=self.foreColor, width=self.size)
        self.yesno.set(0)
        self.end.append(self.lastDraw)

    def onRightButtonUp(self, event):
        """鼠标右键释放事件"""
        pass

    def Open(self):
        """打开图片文件"""
        filename = tk.filedialog.askopenfilename(
            title='导入图片',
            filetypes=[('图片文件', '*.jpg *.png *.gif *jpeg *.bmp')])
        if filename:
            try:
                img = Image.open(filename)
                img = img.resize((self.x, self.y), Image.Resampling.LANCZOS)
                self.image = ImageTk.PhotoImage(img)
                self.canvas.create_image(self.x // 2, self.y // 2, image=self.image)

                # 记录导入的图片
                self.draw_operations.append({
                    'type': 'image',
                    'path': filename,
                    'width': self.x,
                    'height': self.y
                })
            except Exception as e:
                tk.messagebox.showerror("错误", f"无法打开图片: {e}")

    def Save(self):
        """保存画布内容"""
        self.getter()

    def Clear(self):
        """清空画布"""
        for item in self.canvas.find_all():
            self.canvas.delete(item)
        self.end = [0]
        self.lastDraw = 0
        self.draw_operations = []  # 清空绘制操作记录
        if self.erase_cursor:
            self.canvas.delete(self.erase_cursor)
            self.erase_cursor = None

    def Back(self):
        """撤销上一步操作"""
        try:
            for i in range(self.end[-2], self.end[-1] + 1):
                self.canvas.delete(i)
            self.end.pop()

            # 移除最后一次操作的记录
            if self.draw_operations:
                # 找到最后一个非临时操作
                for i in reversed(range(len(self.draw_operations))):
                    op = self.draw_operations[i]
                    if op['type'] != 'pencil' and op['type'] != 'erase':
                        self.draw_operations = self.draw_operations[:i]
                        break
        except:
            self.end = [0]
            self.draw_operations = []

    def drawCurve(self):
        """选择铅笔工具"""
        self.what.set(1)
        if self.erase_cursor:
            self.canvas.delete(self.erase_cursor)
            self.erase_cursor = None

    def drawLine(self):
        """选择直线工具"""
        self.what.set(2)
        if self.erase_cursor:
            self.canvas.delete(self.erase_cursor)
            self.erase_cursor = None

    def drawRectangle(self):
        """选择矩形工具"""
        self.what.set(3)
        if self.erase_cursor:
            self.canvas.delete(self.erase_cursor)
            self.erase_cursor = None

    def drawText(self):
        """选择文本工具"""
        self.text = simpledialog.askstring(title='输入文本', prompt='')
        if self.text is not None:
            new_size = simpledialog.askinteger('输入字号', prompt='', initialvalue=self.size)
            if new_size is not None:
                self.size = new_size
        self.what.set(4)
        if self.erase_cursor:
            self.canvas.delete(self.erase_cursor)
            self.erase_cursor = None

    def onErase(self):
        """选择橡皮擦工具"""
        self.what.set(5)

        erase_window = tk.Toplevel(self.app)
        erase_window.title("橡皮擦大小调节")
        erase_window.geometry("300x100")
        erase_window.resizable(False, False)

        slider = tk.Scale(
            erase_window,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            length=250,
            label="橡皮擦大小:",
            command=lambda v: self.set_erase_size(int(v))
        )
        slider.set(self.erase_size)
        slider.pack(pady=10)

        close_btn = tk.Button(
            erase_window,
            text="确定",
            command=erase_window.destroy
        )
        close_btn.pack()

    def set_erase_size(self, new_size):
        """设置橡皮擦大小"""
        self.erase_size = new_size
        # 如果当前正在使用橡皮擦，更新光标大小
        if self.what.get() == 5:
            # 获取当前鼠标位置
            x, y = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx(), self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            self.update_erase_cursor(x, y)

    def setPenSize(self):
        """设置画笔大小"""
        pen_window = tk.Toplevel(self.app)
        pen_window.title("画笔大小调节")
        pen_window.geometry("300x100")
        pen_window.resizable(False, False)

        slider = tk.Scale(
            pen_window,
            from_=1,
            to=50,
            orient=tk.HORIZONTAL,
            length=250,
            label="画笔大小:",
            command=lambda v: self.set_pen_size(int(v))
        )
        slider.set(self.size)
        slider.pack(pady=10)

        close_btn = tk.Button(
            pen_window,
            text="确定",
            command=pen_window.destroy
        )
        close_btn.pack()

    def set_pen_size(self, new_size):
        """设置画笔大小"""
        self.size = new_size

    def drawCircle(self):
        """选择圆形工具"""
        self.what.set(6)
        if self.erase_cursor:
            self.canvas.delete(self.erase_cursor)
            self.erase_cursor = None

    def chooseForeColor(self):
        """选择前景色"""
        color = colorchooser.askcolor(title='选择前景色', initialcolor=self.foreColor)
        if color[1]:
            self.foreColor = color[1]

    def chooseBackColor(self):
        """选择背景色"""
        color = colorchooser.askcolor(title='选择背景色', initialcolor=self.backColor)
        if color[1]:
            self.backColor = color[1]
            self.canvas.config(bg=self.backColor)

    def getter(self):
        """保存画布内容为图片"""
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )

        if filename:
            try:
                ImageGrab.grab(bbox=(x, y, x + width, y + height)).save(filename)
                tk.messagebox.showinfo("成功", f"图片已保存至: {filename}")
            except Exception as e:
                tk.messagebox.showerror("错误", f"保存失败: {str(e)}")

    def save_canvas_to_temp(self):
        """保存画布内容到临时文件"""
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        try:
            ImageGrab.grab(bbox=(x, y, x + width, y + height)).save(self.temp_canvas_path)
            return True
        except Exception as e:
            tk.messagebox.showerror("错误", f"保存画布失败: {str(e)}")
            return False

    def save_by_pil(self):
        """通过创建PIL.Image对象并绘制Canvas内容来保存"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )

        if filename:
            try:
                # 创建与Canvas大小相同的空白PIL图像
                img = Image.new('RGB', (self.canvas.winfo_width(), self.canvas.winfo_height()), self.backColor)
                draw = ImageDraw.Draw(img)

                # 重绘所有操作到PIL图像
                for op in self.draw_operations:
                    if op['type'] == 'pencil':
                        draw.ellipse(
                            [
                                op['x'] - op['size'] // 2,
                                op['y'] - op['size'] // 2,
                                op['x'] + op['size'] // 2,
                                op['y'] + op['size'] // 2
                            ],
                            fill=op['fill'],
                            outline=op['fill']
                        )
                    elif op['type'] == 'line':
                        draw.line(
                            [op['x1'], op['y1'], op['x2'], op['y2']],
                            fill=op['fill'],
                            width=op['width']
                        )
                    elif op['type'] == 'rectangle':
                        draw.rectangle(
                            [op['x1'], op['y1'], op['x2'], op['y2']],
                            outline=op['outline'],
                            width=op['width']
                        )
                    elif op['type'] == 'oval':
                        draw.ellipse(
                            [op['x1'], op['y1'], op['x2'], op['y2']],
                            outline=op['outline'],
                            width=op['width']
                        )
                    elif op['type'] == 'text':
                        draw.text(
                            (op['x'], op['y']),
                            op['text'],
                            fill=op['fill'],
                            font=op['font']
                        )
                    elif op['type'] == 'erase':
                        draw.ellipse(
                            [
                                op['x'] - op['size'] // 2,
                                op['y'] - op['size'] // 2,
                                op['x'] + op['size'] // 2,
                                op['y'] + op['size'] // 2
                            ],
                            fill=self.backColor,
                            outline=self.backColor
                        )
                    elif op['type'] == 'image':
                        try:
                            # 尝试加载并绘制导入的图片
                            img_obj = Image.open(op['path']).resize((op['width'], op['height']))
                            img.paste(img_obj, (0, 0))
                        except:
                            # 如果图片无法加载，绘制一个占位符
                            draw.rectangle([0, 0, op['width'], op['height']], fill="#CCCCCC")
                            draw.text((op['width'] // 2, op['height'] // 2), "图片加载失败", fill="red")

                # 保存图像
                img.save(filename)
                self.messagebox.showinfo("成功", f"图片已保存至: {filename}")

            except Exception as e:
                self.messagebox.showerror("错误", f"保存失败: {str(e)}")

    def calculate_similarity(self, compare_path, device='cpu'):
        """计算画布内容与选题图片的相似度"""
        # 通过PIL重绘画布
        img = Image.new('RGB', (self.canvas.winfo_width(), self.canvas.winfo_height()), self.backColor)
        draw = ImageDraw.Draw(img)

        # 重绘所有操作到PIL图像
        for op in self.draw_operations:
            if op['type'] == 'pencil':
                draw.ellipse(
                    [
                        op['x'] - op['size'] // 2,
                        op['y'] - op['size'] // 2,
                        op['x'] + op['size'] // 2,
                        op['y'] + op['size'] // 2
                    ],
                    fill=op['fill'],
                    outline=op['fill']
                )
            elif op['type'] == 'line':
                draw.line(
                    [op['x1'], op['y1'], op['x2'], op['y2']],
                    fill=op['fill'],
                    width=op['width']
                )
            elif op['type'] == 'rectangle':
                draw.rectangle(
                    [op['x1'], op['y1'], op['x2'], op['y2']],
                    outline=op['outline'],
                    width=op['width']
                )
            elif op['type'] == 'oval':
                draw.ellipse(
                    [op['x1'], op['y1'], op['x2'], op['y2']],
                    outline=op['outline'],
                    width=op['width']
                )
            elif op['type'] == 'text':
                draw.text(
                    (op['x'], op['y']),
                    op['text'],
                    fill=op['fill'],
                    font=op['font']
                )
            elif op['type'] == 'erase':
                draw.ellipse(
                    [
                        op['x'] - op['size'] // 2,
                        op['y'] - op['size'] // 2,
                        op['x'] + op['size'] // 2,
                        op['y'] + op['size'] // 2
                    ],
                    fill=self.backColor,
                    outline=self.backColor
                )
            elif op['type'] == 'image':
                try:
                    # 尝试加载并绘制导入的图片
                    img_obj = Image.open(op['path']).resize((op['width'], op['height']))
                    img.paste(img_obj, (0, 0))
                except:
                    # 如果图片无法加载，绘制一个占位符
                    draw.rectangle([0, 0, op['width'], op['height']], fill="#CCCCCC")
                    draw.text((op['width'] // 2, op['height'] // 2), "图片加载失败", fill="red")

        # 保存重绘后的图像到临时文件
        img.save(self.temp_pil_path)

        try:
            from compare import calculate_sketch_similarity
            similarity_score = calculate_sketch_similarity(self.temp_pil_path, compare_path, device=device)
            similarity_per = similarity_score * 100

            # 显示结果
            result_window = tk.Toplevel(self.app)
            result_window.title("相似度结果")
            result_window.geometry("400x500")

            tk.Label(result_window, text="相似度分析结果", font=("SimHei", 16, "bold")).pack(pady=15)

            # 显示原图和画布预览
            preview_frame = tk.Frame(result_window)
            preview_frame.pack(fill=tk.X, padx=10, pady=10)

            # 原图预览
            img = Image.open(compare_path)
            img = img.resize((180, 120), Image.Resampling.LANCZOS)
            original_photo = ImageTk.PhotoImage(img)

            original_frame = tk.Frame(preview_frame)
            original_frame.pack(side=tk.LEFT, padx=5)
            tk.Label(original_frame, text="原图", font=("SimHei", 10)).pack()
            tk.Label(original_frame, image=original_photo).pack()
            original_frame.image = original_photo

            # 画布预览
            canvas_img = Image.open(self.temp_pil_path)
            canvas_img = canvas_img.resize((180, 120), Image.Resampling.LANCZOS)
            canvas_photo = ImageTk.PhotoImage(canvas_img)

            canvas_frame = tk.Frame(preview_frame)
            canvas_frame.pack(side=tk.RIGHT, padx=5)
            tk.Label(canvas_frame, text="你的绘制", font=("SimHei", 10)).pack()
            tk.Label(canvas_frame, image=canvas_photo).pack()
            canvas_frame.image = canvas_photo

            # 相似度结果
            tk.Label(result_window, text=f"综合相似度: {similarity_per:.2f}%",
                     font=("SimHei", 20, "bold"), fg="#008000").pack(pady=10)

            # 解释文本（根据相似度分数提供不同的反馈）
            if similarity_per >= 85:
                explanation = "惊人的相似度！你的绘画技巧非常出色，几乎完美还原了原图的结构和细节！"
            elif similarity_per >= 75:
                explanation = "非常相似！你已经很好地把握了原图的主要特征和结构，只需微调一些细节即可。"
            elif similarity_per >= 65:
                explanation = "比较相似，你已经抓住了原图的核心特征，但在比例或细节处理上还有提升空间。"
            elif similarity_per >= 50:
                explanation = "有一定相似度，基本结构已经呈现，但需要在线条流畅度和形状准确性上多下功夫。"
            else:
                explanation = "相似度较低，建议仔细观察原图的比例、结构和关键特征，多练习基础线条。"

            tk.Label(result_window, text=explanation, font=("SimHei", 12), wraplength=350).pack(pady=5)

            # 相似度分布可视化
            similarity_frame = tk.Frame(result_window)
            similarity_frame.pack(fill=tk.X, padx=20, pady=10)

            tk.Label(similarity_frame, text="特征匹配度:", font=("SimHei", 10)).pack(anchor=tk.W)

            # 创建一个水平进度条效果
            progress_bar = tk.Canvas(similarity_frame, height=20, width=300, bg="#f0f0f0")
            progress_bar.pack(fill=tk.X, pady=5)

            # 计算不同颜色区域的宽度
            cos_width = int(300 * 0.6)  # 余弦相似度部分
            ssim_width = int(300 * 0.4)  # SSIM部分

            # 绘制进度条背景
            progress_bar.create_rectangle(0, 0, 300, 20, fill="#e0e0e0", outline="")

            # 绘制余弦相似度部分（蓝色）
            cos_value = 0.4 * similarity_score / similarity_per * 100
            progress_bar.create_rectangle(0, 0, cos_width * cos_value, 20, fill="#4a86e8", outline="")

            # 绘制SSIM部分（绿色）
            ssim_value = 0.6 * similarity_score / similarity_per * 100
            progress_bar.create_rectangle(cos_width, 0, cos_width + ssim_width * ssim_value, 20, fill="#6aa84f", outline="")

            # 添加标签说明
            tk.Label(similarity_frame, text="特征匹配度 (60%)                         结构相似度 (40%)",
                     font=("SimHei", 9)).pack(anchor=tk.W)

        except Exception as e:
            tk.messagebox.showerror("错误", f"相似度计算失败: {str(e)}")

    def show_image(self, image_path, title=None):
        """显示图片并记录当前图片路径"""
        try:
            img = Image.open(image_path)
            img_width, img_height = img.size

            # 调整图片大小以适应窗口
            max_size = 500
            if img_width > max_size or img_height > max_size:
                ratio = min(max_size / img_width, max_size / img_height)
                img = img.resize((int(img_width * ratio), int(img_height * ratio)), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img)

            new_window = tk.Toplevel(self.app)
            new_window.title(title or f"图片: {os.path.basename(image_path)}")

            frame = tk.Frame(new_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 图片显示区域
            label = tk.Label(frame, image=photo)
            label.image = photo
            label.pack(pady=10)

            # 添加比对按钮
            compare_btn = tk.Button(frame, text="与当前画布比对", command=lambda: self.calculate_similarity(image_path),
                                   font=("SimHei", 10), bg="#4CAF50", fg="white", padx=10, pady=5)
            compare_btn.pack(pady=10)

        except Exception as e:
            tk.messagebox.showerror("错误", f"无法打开图片: {str(e)}")

