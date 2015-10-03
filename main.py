#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
import GUI
from GUI import settings, _

root = GUI.tk.Tk()
app = GUI.App(root)
GUI.app = app
root.mainloop()

'''
TODO:
    1. Decoupling.
    2. Add more comments.
    3. "fromstring" is not prefered in Image module.
    4. Read image more diectly.
    5. Image cache, avoid reading and processing image again and again.

'''