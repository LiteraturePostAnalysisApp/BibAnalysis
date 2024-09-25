import os
import tkinter as tk
from tkinter import filedialog
from gptpdf import parse_pdf

def test_use_api_key(pdf_path: str, output_dir: str):
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_API_BASE', "https://api.deepbricks.ai/v1/")
    
    # 调用 parse_pdf 函数进行 PDF 解析
    content, image_paths = parse_pdf(
        pdf_path,
        output_dir=output_dir,
        api_key=api_key,
        base_url=base_url,
        model='gpt-4o',
        gpt_worker=6
    )

if __name__ == "__main__":
    # 创建隐藏的主窗口
    root = tk.Tk()
    root.withdraw()
    
    # 打开文件对话框选择 PDF 文件
    pdf_path = filedialog.askopenfilename(title="选择PDF文件", filetypes=[("PDF文件", "*.pdf")])
    
    if not pdf_path:
        print("未选择文件")
        exit()
    
    # 使用 PDF 文件的名称创建新的输出文件夹
    pdf_file_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.join(os.path.dirname(pdf_path), pdf_file_name)

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    test_use_api_key(pdf_path, output_dir)
