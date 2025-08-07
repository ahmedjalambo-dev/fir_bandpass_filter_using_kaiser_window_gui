import tkinter as tk
from gui import FIRFilterGUI


def main():
    root = tk.Tk()
    app = FIRFilterGUI(root)

    def on_closing():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
