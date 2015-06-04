#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
import GUI
from GUI import settings, _

root = GUI.tk.Tk()
app = GUI.App(root)
GUI.app = app
root.mainloop()