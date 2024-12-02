from tkinter import ttk


def configure_styles():
    """アプリケーション全体のスタイル設定"""
    style = ttk.Style()
    style.configure("Custom.TButton", padding=10, font=("Helvetica", 11))


def create_title_label(parent):
    """タイトルラベルの作成"""
    return ttk.Label(parent, text="Screen OCR Tool", font=("Helvetica", 16, "bold"))


def create_button(parent, text, command, width=25):
    """共通のボタンスタイルで作成"""
    return ttk.Button(
        parent, text=text, command=command, style="Custom.TButton", width=width
    )


STATUS_COLORS = {
    "success": "#4CAF50",  # 緑色
    "processing": "#1976D2",  # 青色
    "error": "#F44336",  # 赤色
}
