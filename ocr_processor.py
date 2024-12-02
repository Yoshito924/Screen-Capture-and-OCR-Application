import easyocr
import numpy as np
import re
from PIL import ImageGrab
import logging

# EasyOCRのログレベルを調整
logging.getLogger("easyocr.easyocr").setLevel(logging.ERROR)


class OCRProcessor:
    def __init__(self):
        try:
            # EasyOCRの初期化（GPU関連の警告を抑制）
            self.reader = easyocr.Reader(["ja", "en"], verbose=False)
        except Exception as e:
            print(f"OCRエンジンの初期化中にエラーが発生しました: {str(e)}")
            raise

    def capture_screen(self, x1, y1, x2, y2):
        """指定された範囲のスクリーンショットを取得"""
        return ImageGrab.grab(bbox=(x1, y1, x2, y2))

    def process_image(self, image):
        """画像からテキストを抽出"""
        img_np = np.array(image)
        return self.reader.readtext(img_np)

    def format_text(self, text_list):
        """OCRテキストのフォーマット処理"""
        # OCR結果のテキストのみを抽出
        texts = [result[1] for result in text_list]

        # 文字列を結合
        text = " ".join(texts)

        # 日本語文字の前後の空白を削除
        text = re.sub(r"([^\x01-\x7E]) ", r"\1", text)  # 日本語文字の後の空白を削除
        text = re.sub(r" ([^\x01-\x7E])", r"\1", text)  # 日本語文字の前の空白を削除

        # 句読点や記号の前後の空白を削除して改行を追加
        text = re.sub(r" ?([。．.!\?！？、,\n]) ?", r"\1\n", text)

        # 連続する改行を1つにまとめる
        text = re.sub(r"\n+", "\n", text)

        # 各行の先頭と末尾の空白を削除
        text = re.sub(r"^ +| +$", "", text, flags=re.MULTILINE)

        # 残りの連続する空白を1つに
        text = re.sub(r"\s+", " ", text)

        return text.strip()
