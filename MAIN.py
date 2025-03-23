import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from paddleocr import PaddleOCR
import ollama 

class OCR_PJ:
    def ocr(img_path):
        print("starting ocr......")
        ocr = PaddleOCR(lang='ch')
        s=""
        result = ocr.ocr(img_path, cls=False)
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                print(line[1][0],end='')
                s+=line[1][0]
        print("\nasking....")
        ts="一个小学生找你批改他的作文，你要对这个作文进行评价，要对一些句子进行润色，批改完成后他会给你一些钱作为奖励，接下来是作文内容：\n"
        res=ollama.chat(model="qwen2.5:14b",stream=False,messages=[{"role": "user","content": ts+s}],options={"temperature":0})
        print(res)
        l=[]
        l.append(s)
        l.append(res['message']['content'])
        ts='请你评价一下这篇作文:\n'
        res=ollama.chat(model="qwen2.5:14b",stream=False,messages=[{"role": "user","content": ts+s}],options={"temperature":0})
        print(res)
        l.append(res['message']['content'])
        return l

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR识别工具 v1.0")
        self.root.geometry("900x600")
        
        # 创建显式可见的控件
        self.create_widgets()
        self.setup_layout()
        
        # 初始化变量
        self.image_path = None

    def create_widgets(self):
        # 顶部按钮区域
        self.top_frame = ttk.Frame(self.root)
        self.btn_open = ttk.Button(self.top_frame, text="打开图片", command=self.open_image)
        self.btn_ocr = ttk.Button(self.top_frame, text="开始识别", command=self.process_image)
        self.btn_clear = ttk.Button(self.top_frame, text="清空结果", command=self.clear_all)

        # 图片显示区域
        self.img_frame = ttk.Frame(self.root)
        self.image_label = tk.Label(self.img_frame, bg="#e0e0e0", relief="sunken")
        
        # 结果展示区域
        self.result_frame = ttk.Frame(self.root)
        self.text_result = tk.Text(self.result_frame, wrap=tk.WORD, font=("微软雅黑", 11))
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.text_result.yview)
        self.text_result.configure(yscrollcommand=self.scrollbar.set)

        #状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor=tk.W)

    def setup_layout(self):
        # 顶部按钮布局
        self.top_frame.pack(pady=10, fill=tk.X)
        self.btn_open.pack(side=tk.LEFT, padx=5)
        self.btn_ocr.pack(side=tk.LEFT, padx=5)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # 图片区域布局
        self.img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        # 结果区域布局
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.text_result.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 状态栏布局
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_image(self):
        filetypes = (
            ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("所有文件", "*.*")
        )
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            try:
                self.image_path = path
                img = Image.open(path)
                img.thumbnail((800, 600))  # 调整图片显示尺寸
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo)
                self.image_label.image = photo  # 保持图片引用
                self.status_var.set(f"已加载图片：{path}")
            except Exception as e:
                self.status_var.set(f"错误：{str(e)}")

    def process_image(self):
        if not self.image_path:
            self.status_var.set("请先选择图片文件")
            return
        

        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, "识别并批改中.....")

        text=OCR_PJ.ocr(self.image_path)
        texts=text[0]+'\n---------------------\n'+text[1]+'\n---------------------\n'+text[2]+'\n'
        #texts = OCR_PJ.ocr(img_path=self.image_path)

        self.text_result.delete(1.0, tk.END)
        self.text_result.insert(tk.END, texts)
        self.status_var.set("识别完成！")

    def clear_all(self):
        self.image_path = None
        self.image_label.config(image=None)
        self.image_label.image = None
        self.text_result.delete(1.0, tk.END)
        self.status_var.set("已重置所有内容")

if __name__ == "__main__":
    # 检测Tkinter支持
    try:
        root = tk.Tk()
        OCRApp(root)
        root.mainloop()
    except tk.TclError:
        print("错误：缺少Tkinter支持！请执行以下操作：")
        print("Ubuntu/Debian: sudo apt install python3-tk")
        print("CentOS/RHEL: sudo yum install python3-tkinter")
        print("Windows/macOS: 应已自带支持")         
