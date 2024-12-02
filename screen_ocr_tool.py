import tkinter as tk
from screen_ocr_app import ScreenOCRApp


def main():
    root = tk.Tk()
    app = ScreenOCRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
