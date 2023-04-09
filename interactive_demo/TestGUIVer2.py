import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class InteractiveSegmentation(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.initUI()

    def initUI(self):
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.grid(column=0, row=0, sticky="nsew")
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)

        self.canvas_container = ttk.Frame(self.canvas_frame)
        self.canvas_container.grid(column=0, row=0, sticky="nsew")
        self.canvas_container.columnconfigure(0, weight=1)
        self.canvas_container.rowconfigure(0, weight=1)

        self.canvas = None
        self.red_square = None

        self.create_canvas()

    def create_canvas(self):
        # Create a separate Tk object for the canvas
        self.canvas_tk = tk.Tk()
        self.canvas_tk.withdraw()

        # Create the canvas
        self.canvas = TkinterCanvas(self.canvas_container, width=500, height=500, bg='white', highlightthickness=0)
        self.canvas.grid(column=0, row=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if self.red_square is None:
            self.red_square = self.canvas.create_rectangle(50, 50, 300, 300, fill='red')
        else:
            self.canvas.delete(self.red_square)
            self.red_square = None


class TkinterCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Configure>", self.resize)

    def resize(self, event):
        self.config(width=event.width, height=event.height)


if __name__ == '__main__':
    root = tk.Tk()
    gui = InteractiveSegmentation(root)
    gui.grid(column=0, row=0, sticky="nsew")
    gui.columnconfigure(0, weight=1)
    gui.rowconfigure(0, weight=1)
    root.mainloop()
