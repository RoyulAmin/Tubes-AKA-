import tkinter as tk #Run GUI Pyramid
from gui.pyramid_gui import PyramidGUI
from stats_manager import catat_permainan

def main():
    root = tk.Tk()
    app = PyramidGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
