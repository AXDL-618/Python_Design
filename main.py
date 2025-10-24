import tkinter as tk
from draw import DrawBoard
import torch

def center_window(w, h):
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    x = (screen_width - w) // 2
    y = (screen_height - h) // 2
    app.geometry(f'{w}x{h}+{x}+{y}')


if __name__ == "__main__":
    app = tk.Tk()
    app.resizable(False, False)
    app.title('画图板工具')
    x = 1200
    y = 800

    # 确保中文显示正常
    font_config = ("SimHei", 10)
    app.option_add("*Font", font_config)

    # 居中窗口
    center_window(x, y)

    # 检测设备
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")

    draw_board = DrawBoard(app, x, y)

    # 创建菜单
    menu = tk.Menu(app)
    app.config(menu=menu)

    # 文件菜单
    file_menu = tk.Menu(menu, tearoff=0)
    file_menu.add_command(label='导入', command=draw_board.Open)
    file_menu.add_command(label='保存', command=draw_board.save_by_pil)
    file_menu.add_command(label='退出', command=app.quit)
    menu.add_cascade(label='文件', menu=file_menu)

    # 工具菜单
    tool_menu = tk.Menu(menu, tearoff=0)
    tool_menu.add_command(label='铅笔', command=draw_board.drawCurve)
    tool_menu.add_command(label='直线', command=draw_board.drawLine)
    tool_menu.add_command(label='矩形', command=draw_board.drawRectangle)
    tool_menu.add_command(label='圆形', command=draw_board.drawCircle)
    tool_menu.add_command(label='文本', command=draw_board.drawText)
    tool_menu.add_command(label='橡皮擦', command=draw_board.onErase)
    tool_menu.add_separator()
    tool_menu.add_command(label='设置画笔大小', command=draw_board.setPenSize)
    tool_menu.add_separator()
    tool_menu.add_command(label='撤销', command=draw_board.Back)
    tool_menu.add_command(label='清屏', command=draw_board.Clear)
    tool_menu.add_command(label='选择前景色', command=draw_board.chooseForeColor)
    tool_menu.add_command(label='选择背景色', command=draw_board.chooseBackColor)
    menu.add_cascade(label='工具', menu=tool_menu)

    # 选题菜单
    t_menu = tk.Menu(menu, tearoff=0)
    # 低难度子菜单
    low_difficulty_menu = tk.Menu(t_menu, tearoff=0)
    low_difficulty_menu.add_command(
        label='小花',
        command=lambda: draw_board.show_image("./db/easy/小花.jpg", "花")
    )
    low_difficulty_menu.add_command(
        label='客机',
        command=lambda: draw_board.show_image("./db/easy/客机.jpg", "客机")
    )
    low_difficulty_menu.add_command(
        label='老鼠',
        command=lambda: draw_board.show_image("./db/easy/老鼠.jpg", "老鼠")
    )
    low_difficulty_menu.add_command(
        label='汽车',
        command=lambda: draw_board.show_image("./db/easy/汽车.jpeg", "汽车")
    )
    low_difficulty_menu.add_command(
        label='鸽子',
        command=lambda: draw_board.show_image("./db/easy/鸽子.jpeg", "鸽子")
    )
    low_difficulty_menu.add_command(
        label='直升机',
        command=lambda: draw_board.show_image("./db/easy/直升机.jpg", "直升机")
    )

    # 高难度子菜单
    high_difficulty_menu = tk.Menu(t_menu, tearoff=0)
    high_difficulty_menu.add_command(
        label='花',
        command=lambda: draw_board.show_image("./db/hard/花.jpg", "花")
    )
    high_difficulty_menu.add_command(
        label='鹤',
        command=lambda: draw_board.show_image("./db/hard/鹤.jpg", "鹤")
    )
    high_difficulty_menu.add_command(
        label='鹊',
        command=lambda: draw_board.show_image("./db/hard/鹊.jpg", "鹊")
    )
    high_difficulty_menu.add_command(
        label='竹',
        command=lambda: draw_board.show_image("./db/hard/竹.jpg", "竹")
    )
    high_difficulty_menu.add_command(
        label='蝶',
        command=lambda: draw_board.show_image("./db/hard/蝶.jpg", "蝶")
    )

    # 将子菜单添加到主菜单
    t_menu.add_cascade(label='低难度', menu=low_difficulty_menu)
    t_menu.add_cascade(label='高难度', menu=high_difficulty_menu)
    t_menu.add_separator()
    menu.add_cascade(label='选题(参照)', menu=t_menu)

    # 添加状态栏
    status_bar = tk.Label(app,
                          text=f"画笔大小: {draw_board.size}  |  橡皮擦大小: {draw_board.erase_size}  |  颜色: {draw_board.foreColor}",
                          bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    app.mainloop()