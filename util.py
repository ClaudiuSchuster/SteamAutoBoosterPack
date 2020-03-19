import os, sys
from PyQt5.QtGui import QTextCursor

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class print_log():
    def __init__(self,label_obj,max_len = 1000):
        self.container = []
        self.max_len = max_len
        self.label_obj = label_obj
    def append(self,text,out=False,color="#000000"):
        self.container.append(f"<font color='{color}'>{text}</font>")
        if len(self.container)>self.max_len:
            self.container.pop(0)
        if out:
            self.text_out()
    def text_out(self):
        text = '<br/>'.join(self.container)
        self.label_obj.setText(text)
        self.label_obj.repaint()
        self.label_obj.moveCursor(QTextCursor.End)
        self.label_obj.ensureCursorVisible()