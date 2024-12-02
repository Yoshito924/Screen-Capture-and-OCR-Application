import tkinter as tk
from tkinter import ttk, messagebox
import ui_components as ui
from ocr_processor import OCRProcessor
import json
import os

class ScreenOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen OCR Tool")
        
        # 設定ファイルのパス
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'window_config.json')
        
        # 前回のウィンドウ設定を読み込む
        self.load_window_config()
        
        self.ocr_processor = OCRProcessor()
        self.init_variables()
        self.create_widgets()
        
        # ウィンドウ位置が保存されていれば適用
        if hasattr(self, 'window_geometry'):
            self.root.geometry(self.window_geometry)
        else:
            # デフォルトサイズと位置
            self.root.geometry("800x600+100+100")
        
        # 最小サイズを設定
        self.root.minsize(800, 600)
        
        # ウィンドウが閉じられる時のイベントをバインド
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # ウィンドウサイズ変更の監視を開始
        self.root.bind('<Configure>', self.on_window_configure)
        
        self.root.after(2000, self.initialization_complete)

    def load_window_config(self):
        """前回のウィンドウ設定を読み込む"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.window_geometry = config.get('geometry')
        except Exception as e:
            print(f"設定の読み込みに失敗しました: {str(e)}")

    def save_window_config(self):
        """現在のウィンドウ設定を保存"""
        try:
            config = {
                'geometry': self.root.geometry()
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"設定の保存に失敗しました: {str(e)}")

    def on_window_configure(self, event):
        """ウィンドウのサイズや位置が変更された時の処理"""
        if event.widget == self.root and self.root.state() == 'normal':
            # 最小化やフルスクリーン時は保存しない
            self.save_window_config()

    def on_closing(self):
        """ウィンドウが閉じられる時の処理"""
        self.save_window_config()
        self.root.destroy()

    def init_variables(self):
        """変数の初期化"""
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selection_rect = None

    def create_widgets(self):
        """ウィジェットの作成"""
        ui.configure_styles()
        self.create_main_frame()
        self.create_title()
        self.create_buttons()
        self.create_text_area()
        self.create_status_bar()

    def create_main_frame(self):
        """メインフレームの作成"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

    def create_title(self):
        """タイトルの作成"""
        title_label = ui.create_title_label(self.main_frame)
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

    def create_buttons(self):
        """ボタンの作成"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        self.capture_btn = ui.create_button(
            button_frame,
            "OCRする領域を選択",
            self.start_capture
        )
        self.capture_btn.pack(side=tk.LEFT, padx=5)

        self.copy_btn = ui.create_button(
            button_frame,
            "OCRしたテキストをコピー",
            self.copy_to_clipboard
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)

    def create_text_area(self):
        """テキストエリアの作成"""
        text_frame = ttk.Frame(self.main_frame)
        text_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        self.text_area = tk.Text(
            text_frame,
            height=20,
            font=('Helvetica', 11),
            wrap=tk.WORD,
            padx=5,
            pady=10
        )
        self.text_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(
            text_frame,
            orient="vertical",
            command=self.text_area.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_area["yscrollcommand"] = scrollbar.set

    def create_status_bar(self):
        """ステータスバーの作成"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        self.status_label = tk.Label(
            status_frame,
            text="初期化中...",
            font=('Helvetica', 9),
            fg=ui.STATUS_COLORS['processing']
        )
        self.status_label.pack(side=tk.LEFT)

    def initialization_complete(self):
        """初期化完了後の処理"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, "ここにキャプチャしたテキストが表示されます")
        self.text_area.config(fg='gray')
        self.update_status("OCRを実行できます", 'success')

    def update_status(self, message, status_type='normal'):
        """ステータスバーの更新"""
        self.status_label.config(
            text=message,
            fg=ui.STATUS_COLORS.get(status_type, '#000000')
        )

    def copy_to_clipboard(self):
        """テキストエリアの内容をクリップボードにコピー"""
        text = self.text_area.get(1.0, tk.END).strip()
        if text == "ここにキャプチャしたテキストが表示されます":
            messagebox.showinfo("コピー", "コピーするテキストがありません")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.update_status("テキストをコピーしました", 'success')
        self.root.after(2000, lambda: self.update_status("OCRを実行できます", 'success'))

    def start_capture(self):
        """画面キャプチャを開始"""
        self.root.iconify()  # ウィンドウを最小化
        self.capture_screen = tk.Toplevel(self.root)
        self.capture_screen.attributes('-fullscreen', True, '-alpha', 0.3)
        self.capture_screen.attributes('-topmost', True)  # 最前面に表示

        self.canvas = tk.Canvas(
            self.capture_screen,
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)

        # マウスイベントをバインド
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        
        # ESCキーでキャプチャをキャンセル
        self.capture_screen.bind('<Escape>', lambda e: self.cancel_capture())
        
        # マウスカーソルをクロスヘアに変更
        self.canvas.config(cursor="crosshair")
        
        # 画面全体に薄い色をオーバーレイ
        self.canvas.create_rectangle(
            0, 0, 
            self.capture_screen.winfo_screenwidth(),
            self.capture_screen.winfo_screenheight(),
            fill='gray', stipple='gray50'
        )

    def cancel_capture(self):
        """キャプチャをキャンセル"""
        if hasattr(self, 'capture_screen'):
            self.capture_screen.destroy()
            self.root.deiconify()

    def on_click(self, event):
        """マウスクリック時の処理"""
        self.start_x = event.x
        self.start_y = event.y

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

    def on_drag(self, event):
        """マウスドラッグ時の処理"""
        self.end_x = event.x
        self.end_y = event.y

        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

        # 選択範囲を表示
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.end_x, self.end_y,
            outline='red',
            width=2
        )
        
        # 選択範囲の座標を表示
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        self.canvas.delete('size_text')
        self.canvas.create_text(
            self.end_x + 10, self.end_y + 10,
            text=f'{width} x {height}',
            fill='red',
            tags='size_text'
        )

    def on_release(self, event):
        """マウスリリース時の処理"""
        self.end_x = event.x
        self.end_y = event.y
        self.capture_screen.destroy()
        self.root.deiconify()

        try:
            # 選択範囲の座標を整理
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)

            # 選択範囲が小さすぎる場合は処理をスキップ
            if abs(x2 - x1) < 10 or abs(y2 - y1) < 10:
                self.update_status("選択範囲が小さすぎます", 'error')
                return

            # スクリーンショットを取得
            screenshot = self.ocr_processor.capture_screen(x1, y1, x2, y2)

            # OCR実行
            self.update_status("OCR処理中...", 'processing')
            results = self.ocr_processor.process_image(screenshot)

            # 結果を表示
            self.text_area.delete(1.0, tk.END)
            self.text_area.config(fg='black')

            if results:
                # OCR結果を整形
                formatted_text = self.ocr_processor.format_text(results)
                self.text_area.insert(tk.END, formatted_text)
                self.update_status("OCR完了", 'success')
                self.root.after(2000, lambda: self.update_status("OCRを実行できます", 'success'))
            else:
                self.text_area.insert(tk.END, "テキストが検出されませんでした。")
                self.update_status("テキストが検出されませんでした", 'error')
                self.root.after(2000, lambda: self.update_status("OCRを実行できます", 'success'))

        except Exception as e:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"エラーが発生しました: {str(e)}")
            self.update_status("エラーが発生しました", 'error')
            self.root.after(2000, lambda: self.update_status("OCRを実行できます", 'success'))