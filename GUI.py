# -*- coding: utf-8 -*-
import dicom#parse dicom file.

import Tkinter as tk#gui.
import ttk#themed Tkinter.
import tkMessageBox#pop up message.
import tkFileDialog#pop up 'ask open file dialog'.
import tkSimpleDialog#ask input ratio.

import os#os name, seperator, isdir, listdir etc.
import ConfigParser#read and save configure.
import shutil#copy file.

#import files.
import languages#multi-language support.
import MRI_canvas as Mc
import MRI_sequence as Ms

class Settings:
    """
    Read configure info from settings.ini.
    """
    def __init__(self):
        self._read_ini()

    def _read_ini(self):
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.read('settings.ini')
        except ConfigParser.MissingSectionHeaderError:
            #BOM in utf-8 file.
            from StringIO import StringIO
            with open('settings.ini', 'rb') as f:
                content = f.read().decode('utf-8-sig').encode('utf8')
                self.config.readfp(StringIO(content))

    def get_language(self):
        try:
            return self.config.get('Languages', 'language')
        except:
            return 'English'

    def set_language(self, string):
        """
        Change interface language.
        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Languages'):
                self.config.add_section('Languages')
            self.config.set('Languages', 'language', string.encode('utf-8'))
            self.config.write(configfile)

    def get_directory(self):
        try:
            return self.config.get('Initial Directory', 'directory')
        except:
            return '/'

    def set_directory(self, string):
        """
        Set initial directory.
        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Initial Directory'):
                self.config.add_section('Initial Directory')
            self.config.set('Initial Directory', 'directory', string.encode('utf-8'))
            self.config.write(configfile)


    def get_window_size(self):
        """
        Get window size.
        """
        try:
            return self.config.get('Window Size', 'wxh')
        except:
            return '700x500'


    def set_window_size(self, string):
        """
        Set initial directory.
        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Window Size'):
                self.config.add_section('Window Size')
            self.config.set('Window Size', 'wxh', string.encode('utf-8'))
            self.config.write(configfile)


    def get_paned_ratio(self):
        """

        """
        try:
            string = self.config.get('Paned Windows Ratio', 'ratio').replace('：', ':')
            return map(int, string.split(':'))
        except:
            return (1, 6)



    def set_paned_ratio(self, string):
        """

        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Paned Windows Ratio'):
                self.config.add_section('Paned Windows Ratio')
            self.config.set('Paned Windows Ratio', 'ratio', string.encode('utf-8'))
            self.config.write(configfile)


    def get_sidebar_max_lines(self):
        """

        """
        try:
            return int(self.config.get('Sidebar Max Lines', 'lines'))
        except:
            return 29


    def set_sidebar_max_lines(self, string):
        """

        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Sidebar Max Lines'):
                self.config.add_section('Sidebar Max Lines')
            self.config.set('Sidebar Max Lines', 'lines', string.encode('utf-8'))
            self.config.write(configfile)

    def get_resize_filter_type(self):
        """

        """
        try:
            type_int = int(self.config.get('Resize Filter Type', 'type'))
            if type_int in (0, 1, 2, 3):
                return type_int
            else:
                return 0
        except:
            return 0

    def get_min_max_zoomfactor(self):
        """

        """
        try:
            min_max = self.config.get('Min Max Zoom Factor', 'min max').split(' ')
            min_max = [float(i) for i in min_max]
            return min_max
        except:
            return [0.05, 6.0]

settings = Settings()


def _(string):
    """
    Return meaning string show on preset language. Need shoten meaning string.
    """
    try:
        return languages.table[settings.get_language()][string]
    except KeyError:
        #if string not found in table
        return "x: " + string

class StatusBar(tk.Frame):
    """
    Status frame derived from tk.Frame. To show info. Can be set and clear.
    """
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self, bd = 1, relief = 'sunken', anchor = 'w', bg = 'black', fg = 'white')
        self.label.pack(fill = 'x', expand = 1)
        self.master = master
    
    def set(self, format, *args):
        """Set message."""
        self.label.config(text = format % args)
        self.label.update_idletasks()
    
    def clear(self):
        """Clear message."""
        self.label.config(text = '')
        self.label.update_idletasks()

    def flash(self, time, format, *args):
        """Show message and clear after a time specified."""
        self.set(format, *args)
        self.after(time, self.clear)

class Dir_frame(tk.Frame):
    """
    A frame display on the left window showing directory.
    """
    def __init__(self, master, abspath):
        tk.Frame.__init__(self, master)
        self.master.update_idletasks()
        self.master = master
        self.m_height = self.master.winfo_height()
        self.abspath = abspath
        self.dir_frame_view()
        self.tree.bind("<Double-1>", self.onDBClick1)
        self.tree.bind("<Double-3>", self.onDBClick3)


    def dir_frame_view(self):
        self.tree = ttk.Treeview(self, show = 'tree', height = settings.get_sidebar_max_lines())#self.master.winfo_height() / 22
        self.ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=self.ysb.set, xscroll=self.xsb.set)
        self.tree.heading('#0', text='Path', anchor='w')
        self.tree.column('#0', stretch = 1, minwidth = int(self.master.winfo_width()*3), width = int(self.master.winfo_width() -24))#

        root_node = self.tree.insert('', 'end', text=self.abspath, open=True)
        self.process_directory(root_node, self.abspath)

        self.tree.grid(row=0, column=0)
        self.ysb.grid(row=0, column=1, sticky='ns')
        self.xsb.grid(row=1, column=0, sticky='we')


    """
    def on_configure(self, event):
        self.master.update_idletasks()
        print('configure')
        print('aaa',int(self.master.master.winfo_width()*4 - 24))
        #self.tree.columnconfigure(0, minsize = int(self.master.winfo_width() - 24))
        self.tree.column('#0', stretch = 1, width = int(self.master.master.winfo_width()*4 - 24))
        #self.tree.grid_columnconfigure(0, width = int(self.master.winfo_width()))
    """
    def process_directory(self, parent, path):
        """
        Process current directory.
        """

        self.tree.delete(*self.tree.get_children(parent))
        try:
            for p in os.listdir(path):
                #create dir content.
                abspath = os.path.join(path, p)
                oid = self.tree.insert(parent, 'end', text=p, open=False)
        #windows access denied exception.
        except:
            pass


    def onDBClick3(self, event):
        """
        Double right click on dir to open series.
        """
        #oid = self.tree.selection()[0]
        oid = self.tree.identify_row(event.y)
        if oid:
            # mouse pointer over item
            self.tree.selection_set(oid)
            #self.contextMenu.post(event.x_root, event.y_root)            
        else:
            # mouse pointer not over item
            # occurs when items do not fill frame
            # no action required
            pass


        
        oid_cpy = oid
        #get absolute path from file/folder name.
        abspath = self.tree.item(oid_cpy, 'text')
        while (self.tree.parent(oid_cpy) != ''):
            oid_parent = self.tree.parent(oid_cpy)
            abspath = os.path.join(self.tree.item(oid_parent, 'text'), abspath)
            oid_cpy = oid_parent

        isdir = os.path.isdir(abspath)
        if isdir:
            #right DB click on folder. for folder, show folder content and open series.
            #open folder and view by generate double left click.
            #self.process_directory(oid, abspath)
            path = abspath
            self.tree.event_generate('<Button-1>', x = event.x, y = event.y)
            self.tree.event_generate('<Button-1>', x = event.x, y = event.y)
        else:
            #right DB click on file. for file, get file parent path for open series.
            path = os.sep.join(abspath.split(os.sep)[:-1])+os.sep
        app.open_series(path = path)

    def onDBClick1(self, event):
        """
        Double left click on dir to open single file or open folder.
        """
        oid = self.tree.selection()[0]
        oid_cpy = oid
        abspath = self.tree.item(oid_cpy, 'text')
        while (self.tree.parent(oid_cpy) != ''):

            oid_parent = self.tree.parent(oid_cpy)
            abspath = os.path.join(self.tree.item(oid_parent, 'text'), abspath)
            oid_cpy = oid_parent

        isdir = os.path.isdir(abspath)
        if isdir:
            self.process_directory(oid, abspath)
        else:
            app.open_file(abspath = abspath)

class Slide_show_ctrl_window:
    def __init__(self, master):
        self.master = master
        self.right = 1
        self.pause = True
        self.scale = None
        self._ctrl_window()

    def _play(self):
        if not self.pause:
            self.master.z_index += self.right
            self.max = self.master.array.shape[0]-1 if len(self.master.array.shape) == 3 else self.master.array.shape[1]-1
            if(self.master.z_index < 0 or self.master.z_index > self.max):
                self._press_pause()
                if self.master.z_index < 0:
                    self.master.z_index = -1
                else:
                    self.master.z_index = self.max
                return
            self.master._display()
            self.master._slice_change_event_generate()
            self.master.after(int(1000 * self.scale.get()), self._play)
        else:
            return
    def _press_left(self):
        if self.right == -1:
            return

        self.right = -1
        if self.pause:
            self._press_pause()

    def _press_right(self):
        if self.right == 1:
            return

        self.right = 1
        if self.pause:
            self._press_pause()

    def _press_pause(self):

        self.pause = not self.pause
        #if self.button_pause['text'] == unicode(_('Start').decode('utf-8')):
        #encoding and decoding are too slow and causing un even switching time.
        if self.button_pause['text'] == 'Start':
            self.button_pause['text'] = 'Pause'
        else:
            self.button_pause['text'] = 'Start'
        self.master.after(int(1000 * self.scale.get()), self._play)


    def _ctrl_window(self):
        self.top_level = tk.Toplevel()
        self.top_level.title(_('Slide show'))
        self.top_level.wm_attributes('-topmost', True)
        self.scale = tk.Scale(self.top_level, from_ = 0.1, to = 1.1, resolution = 0.1, label=_('Speed:'), tickinterval=1, orient='horizontal')
        self.scale.set(0.5)
        self.button_left = tk.Button(self.top_level, text = '<<', command = self._press_left)
        self.button_pause = tk.Button(self.top_level, text = 'Start', command = self._press_pause, width = 5)
        self.button_right = tk.Button(self.top_level, text = '>>', command = self._press_right)

        self.scale.grid(row = 0, column = 0, columnspan = 3)
        self.button_left.grid(row = 1, column = 0)
        self.button_pause.grid(row = 1, column = 1)
        self.button_right.grid(row = 1, column = 2)
        self.top_level.wait_window()


class App:
    def __init__(self, master):
        self.master = master
        self.settings = settings
        #deal with close. 'x' clicked on purpose or unintentionally.
        self.master.protocol('WM_DELETE_WINDOW', self.SafeExit) 
        self.browse_abspath = settings.get_directory() #'D:\\pydicom viewer\\pydicom\\anonymized_data_08272014\\000005'

        self._customize_window()
        self.main()
        self._bind_events()

    def SafeExit(self):
        """
        Save changes before exit.
        """
        if self.c.contour_coors or self.c.text_coors:
            save = tkMessageBox.askyesno(_('TT_Save_ROI_before'),_('MES_Save_ROI_before'))
            if save:
                self.save_ROI()

        root.destroy()##todo

    def _platform(self):
        if 'nt' == os.name:
            return 'Windows'
        else:
            return 'Linux'

    def set_lang(self, string):
        """
        Change interface language.
        """
        self.settings.set_language(string)
        '''
        config = self.settings.config
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not config.has_section('Languages'):
                config.add_section('Languages')
            config.set('Languages', 'language', string.encode('utf-8'))
            config.write(configfile)
        '''
        tkMessageBox.showinfo(string + " selected.", "Restart required to apply changes.")

    def set_dir(self):
        path = tkFileDialog.askdirectory(initialdir = self.settings.get_directory())
        if path == '':
            return

        self.update_dir_frame(path)
        self.settings.set_directory(path)


    def set_win_size(self):
        string = self.scale_get_win_size()
        if string:
            self.master.geometry(string)
            self.settings.set_window_size(string)


    def scale_get_win_size(self):
        string_list = [None]
        top_level = tk.Toplevel()
        top_level.wm_attributes('-topmost', True)
        top_level.title(_('m_set_win_size'))
        xlabel=tk.Label(top_level, text = 'x')
        ylabel=tk.Label(top_level, text = 'y')
        scr_width = self.master.winfo_screenwidth()
        scr_height = self.master.winfo_screenheight()
        xscale=tk.Scale(top_level,from_=10,to=scr_width,resolution=1,tickinterval=300,length=400,orient='horizontal')
        yscale=tk.Scale(top_level,from_=10,to=scr_height,resolution=1,tickinterval=300,length=400,orient='horizontal')

        xscale.set(self.master.winfo_width())
        yscale.set(self.master.winfo_height())

        def _yes_destroy():
            string_list[0] = str(xscale.get()) + 'x' + str(yscale.get())
            top_level.destroy()
        def _no_destroy():
            top_level.destroy()

            
        yes_button = tk.Button(top_level, text = _('OK!'), command = _yes_destroy)
        no_button = tk.Button(top_level, text = _('Cancel...'), command = _no_destroy)


        xlabel.grid(row = 0, column = 0)
        ylabel.grid(row = 1, column = 0)
        xscale.grid(row = 0, column = 1)
        yscale.grid(row = 1, column = 1)
        yes_button.grid(row =0, column = 2)
        no_button.grid(row =1, column = 2)
        
        top_level.protocol('WM_DELETE_WINDOW', _no_destroy)
        top_level.wait_window()
        return string_list[0]


    def set_paned_ratio(self):
        try:
            string = tkSimpleDialog.askstring(_('Paned Windows Ratio'), _('Set ratio, all integers. Left:Right eg. 1:5'), initialvalue = self.settings.config.get('Paned Windows Ratio', 'ratio'))
        except:# NoSectionError:
            string = tkSimpleDialog.askstring(_('Paned Windows Ratio'), _('Set ratio, all integers. Left:Right eg. 1:5'))
        if not string:
            return
        string = string.replace('：', ':')
        self.settings.set_paned_ratio(string)
        self.status.flash(10000, _('Restart to apply panedwindow changes.'))

    def set_sidebar_max_lines(self):
        try:
            string = tkSimpleDialog.askstring(_('Set Sidebar Max Lines'), _('Sidebar max Lines(integer):'), initialvalue = self.settings.config.get('Set Sidebar Max Lines', 'lines'))
        except:# NoSectionError:
            string = tkSimpleDialog.askstring(_('Set Sidebar Max Lines'), _('Sidebar max Lines(integer):'))
        if not string:
            return
        int(string)
        self.settings.set_sidebar_max_lines(string)
        self.update_dir_frame(self.browse_abspath)
        
    def set_contour_color(self):
        if not hasattr(self, 'c'):
            return
        self.c.set_contour_color()

    def set_text_color(self):
        if not hasattr(self, 'c'):
            return
        self.c.set_text_color()

    def set_resize_filter_type(self):
        if not hasattr(self, 'c'):
            return
        self.c.set_resize_filter_type(self.resize_filter_type_int.get())

    def set_min_max_zoomfactor(self):
        if not hasattr(self, 'c'):
            return
        min_max = self.scale_get_min_max_zoomfactor()
        if min_max:
            self.c.set_min_max_zoomfactor(min_max)

    def scale_get_min_max_zoomfactor(self):
        min_max_list = [[]]
        top_level = tk.Toplevel()
        top_level.wm_attributes('-topmost', True)
        top_level.title(_('m_set_min_max_zoomfactor'))
        xlabel=tk.Label(top_level, text = _('min'))
        ylabel=tk.Label(top_level, text = _('max'))

        xscale=tk.Scale(top_level,from_=0.01,to=1,resolution=0.01,tickinterval=0.2,length=400,orient='horizontal')
        yscale=tk.Scale(top_level,from_=1,to=20,resolution=1,tickinterval=5,length=400,orient='horizontal')

        xscale.set(self.settings.get_min_max_zoomfactor()[0])
        yscale.set(self.settings.get_min_max_zoomfactor()[1])

        def _yes_destroy():
            min_max_list[0] = [xscale.get(), yscale.get()]
            top_level.destroy()
        def _no_destroy():
            top_level.destroy()

            
        yes_button = tk.Button(top_level, text = _('OK!'), command = _yes_destroy)
        no_button = tk.Button(top_level, text = _('Cancel...'), command = _no_destroy)


        xlabel.grid(row = 0, column = 0)
        ylabel.grid(row = 1, column = 0)
        xscale.grid(row = 0, column = 1)
        yscale.grid(row = 1, column = 1)
        yes_button.grid(row =0, column = 2)
        no_button.grid(row =1, column = 2)
        
        top_level.protocol('WM_DELETE_WINDOW', _no_destroy)
        top_level.wait_window()
        return min_max_list[0]

    def backup_ini(self):
        tkMessageBox.showinfo(_('manually_backup'), _('ini_location'))
        if 'Windows' == self._platform():
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(None, u'open', u'explorer.exe', 
                                    u'/n,/select, ' + 'settings.ini', None, 1)

    def help(self):
        tkMessageBox.showinfo('', _('user_guide'))


    def contact(self):
        tkMessageBox.showinfo('', _('contact'))

    def open_file(self, abspath = ''):
        """
        Open single file.
        """
        if abspath == '':
            abspath = tkFileDialog.askopenfilename()
            if abspath == '':
                return
        try:
            dicom.read_file(abspath, stop_before_pixels = True)
            #clear previous window.
            for child in self.showbox.winfo_children():#
                child.destroy()
            directory = os.path.split(abspath)[0]#, file 

            seq = Ms.MRI_sequence(directory, files = [abspath])
            seq.read_data()


            self.c = Mc.MRI_canvas(self.showbox, bg = 'black', name = 'show_canvas')
            self.c.seq = seq
            cysb = tk.Scrollbar(self.showbox, orient = 'vertical', command = self.c.yview)
            cxsb = tk.Scrollbar(self.showbox, orient = 'horizontal', command = self.c.xview)
            self.showbox.cysb = cysb
            self.showbox.cxsb = cxsb
            self.c.set_array(self.c.seq.data[0])
            #c.configure(width =  master.winfo_width(), height = master.winfo_height()*0.95-25)
            self.c.configure(yscrollcommand = self.showbox.cysb.set, xscrollcommand = self.showbox.cxsb.set)


            #c.grid(row = 0, column = 0)
            #cysb.grid(row=0, column=1, sticky='ns')
            #cxsb.grid(row=1, column=0, sticky='we')
            self.c.pack(fill = 'both', expand = 1)
            self.showbox.cysb.pack(in_ = self.c, fill = 'y', expand = 1, anchor = 'w', side = 'left')#)#, side = 'left', pady = 50, side = 'right'
            self.showbox.cxsb.pack(in_ = self.c, expand = 1, anchor = 'n')#, side = 'left', side = 'left', side = 'left',anchor = 'se', fill = 'x', anchor = 'w' 
            #c['scrollregion']=c.bound#(0,0,master.winfo_width(),master.winfo_height())

            #c.pack(fill = 'both', expand = 1)
           
            self.showbox.test.pack(in_ = self.c, padx = 4, pady = 4, anchor = 'se')#, anchor = 'nw', side = 'left'

        #if it is an invalid DICOM file.
        except dicom.filereader.InvalidDicomError:
            #prompt message in status bar and vanished within 1s.
            self.status.set(_('invalidDCMerr_msg'))
            self.status.after(1000, self.status.clear)

    def open_series(self, path = ''):
        """
        Open DICOM series.
        """
        if path =='':
            path = tkFileDialog.askdirectory()
            if path == '':
                return

        #clear previous window.
        for child in self.showbox.winfo_children():
            child.destroy()


        seq = Ms.MRI_sequence(path)
        seq.read_data()

        self.c = Mc.MRI_canvas(self.showbox, bg = 'black', name = 'show_canvas')
        self.c.seq = seq
        self.c.set_array(self.c.seq.data)
        #c.pack(fill = 'both', expand = 1)
        cysb = tk.Scrollbar(self.showbox, orient = 'vertical', command = self.c.yview)
        cxsb = tk.Scrollbar(self.showbox, orient = 'horizontal', command = self.c.xview)
        self.showbox.cysb = cysb
        self.showbox.cxsb = cxsb
        self.c.configure(yscrollcommand = self.showbox.cysb.set, xscrollcommand = self.showbox.cxsb.set)

        self.c.pack(fill = 'both', expand = 1)
        self.showbox.cysb.pack(in_ = self.c, fill = 'y', expand = 1, anchor = 'w', side = 'left')#, side = 'left', pady = 50, side = 'right'
        self.showbox.cxsb.pack(in_ = self.c, expand = 1, anchor = 'n')

        self.showbox.test.pack(in_ = self.c, padx = 10, pady = 10, anchor = 'se')#, anchor = 'nw', side = 'left'

    def close_file_s(self):
        for child in self.showbox.winfo_children():
            child.destroy()


    def save_file(self):
        file_name = self.c.file_name

        if file_name == '':
            status.set(_('No file opened.'))
            status.after(1000, lambda : status.clear())
            return
        dst = tkFileDialog.asksaveasfilename(defaultextension=".dcm", filetypes = [('dcm files', '.dcm'), ('all files', '.*')])
        if not dst: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        shutil.copy2(file_name, dst)

    def save_ROI(self):
        #c = showbox.nametowidget('show_canvas')
        if (not self.c.contour_coors) and (not self.c.text_coors):
            return
        initialdir, initialfile = os.path.split(self.c.file_name)
        demention = len(self.c.array.shape)
        if demention == 2:
            initialfile = initialfile + '.single'
        else:
            initialfile = initialfile + '.series'
        name = tkFileDialog.asksaveasfilename(initialdir = initialdir, initialfile = initialfile+'.ROI.txt', defaultextension=".txt", filetypes = [('Text files', '.txt')])
        if name:
            with open(name, 'w') as f:
                f.write('#This file is created by Python DICOM viewer. It contains DICOM file ROI contour and text coordinates infomation.')
                f.write('\n')
                f.write('[contour]')
                f.write(str(self.c.contour_coors))
                f.write('\n')
                f.write('[text]')
                f.write(str(self.c.text_coors))
                f.write('\n')

    def load_ROI(self):
        import ast
        c = self.showbox.nametowidget('show_canvas')
        initialdir = os.path.split(self.c.file_name)[0]
        name = tkFileDialog.askopenfilename(initialdir = initialdir, defaultextension ='.txt', filetypes = [('Text files', '.txt')])
        if not name:
            return
        ext = os.path.splitext(name)[1]
        if ext !='.txt':
            return
        with open(name,'r') as f:
            lines = f.readlines()

            polygon = lines[1][len('[contour]'):]
            text = lines[2][len('[text]'):]

            self.c.contour_coors = ast.literal_eval(polygon)
            self.c.text_coors = ast.literal_eval(text)
            self.c._display_contours()
            self.c._display_text()

    def measure_distance(self):
        self.status.flash(2000, _('Press and drag the middle mouse button to start measuring.'))



    def convert_bmp(self):
        #c=showbox.nametowidget('show_canvas')
        if self.c.array == '':
            return
        dst = tkFileDialog.asksaveasfilename(defaultextension = '.bmp', filetypes = [('bmp files', '.bmp'), ('jpeg files', '.jpg'), ('png files', '.png'), ('gif files', '.gif'), ('photo shop files', '.ps'), ('all files', '.*')])
        if dst == '':
            return
        ext = os.path.splitext(dst)[1]
        if ext == '.ps':
            self.c.postscript(file = dst, colormode = 'color')
        else:
            self.c._display()
            self.c.im.save(dst)

    def convert_all_bmp(self):
        #c=showbox.nametowidget('show_canvas')
        if self.c.array == '' or len(self.c.array.shape) <3:
            return


        def _ask_extention():
            option_list = ('.bmp', '.jpg', '.png', '.gif', '.ps')
            sv = tk.StringVar()
            sv.set(option_list[0])

            top_level = tk.Toplevel()
            top_level.wm_attributes('-topmost', True)
            top_level.title(_('Choose an extension:'))
            label=tk.Label(top_level, text = _('Choose an extension:'))
            label.pack()
            opt_menu = tk.OptionMenu(top_level, sv, *option_list)
            opt_menu.pack(side = 'top')

            def _yes_destroy():
                _ask_extention.cancel = False
                top_level.destroy()
            def _no_destroy():
                _ask_extention.cancel = True
                top_level.destroy()
                

            yes_button = tk.Button(top_level, text = _('OK!'), command = _yes_destroy).pack(side = 'top')
            no_button = tk.Button(top_level, text = _('Cancel...'), command = _no_destroy).pack(side = 'top')

            top_level.protocol('WM_DELETE_WINDOW', _no_destroy)

            top_level.wait_window()
            return sv, _ask_extention.cancel

        sv,cancel = _ask_extention()
        ext = sv.get()
        #print(ext, cancel, "asdf")
        if cancel:
            return
        dst = tkFileDialog.askdirectory()
        if not dst:
            return
        self.c.pack_forget()
        #c.lower(c.master.master)
        #d = tk.Label(c.master, text = 'Processing...', bg = 'black')
        #d.pack(fill = 'both', expand = 1)
        if len(self.c.array.shape)==3:
            for z_index in range(self.c.array.shape[0]):
                self.c.z_index = z_index
                self.c._display()
                self.c._slice_change_event_generate()
                abspath = dst + os.sep + os.path.split(self.c.file_name)[1] + ext
                if ext == '.ps':
                    self.c.postscript(file = abspath, colormode = 'color')
                else:
                    self.c.im.save(abspath)
        elif len(self.c.array.shape)==4:
            for t_index in range(self.c.array.shape[0]):
                for z_index in range(self.c.array.shape[1]):
                    self.c.t_index = t_index
                    self.c.z_index = z_index
                    self.c._display()
                    self.c._slice_change_event_generate()
                    abspath = dst + os.sep + os.path.split(self.c.file_name)[1] + ext
                    if ext == '.ps':
                        self.c.postscript(file = abspath, colormode = 'color')
                    else:
                        self.c.im.save(abspath)
        self.c.pack(fill = 'both', expand = 1)

    def show_tags(self):
        #c = showbox.nametowidget('show_canvas')
        file_name = self.c.file_name
        if file_name == '':
            return
        else:
            import Tix
            import dicomtree
            root2 = Tix.Tk()
            root2.title(file_name)
            root2.geometry("{0:d}x{1:d}+{2:d}+{3:d}".format(800, 650, 0, 0))
            dicomtree.RunTree(root2, file_name)
            root2.mainloop()

    def slide_show(self):
        #c=showbox.nametowidget('show_canvas')
        if self.c.array == '' or len(self.c.array.shape) < 3:
            return
        a = Slide_show_ctrl_window(self.c)


    def update_dir_frame(self, abspath):
        if not abspath:
            return
        self.dir_frame.destroy()
        self.dir_frame = Dir_frame(master = self.sidebar, abspath = abspath)
        self.dir_frame.grid(row = 1, column = 0, columnspan = 3, sticky ='nswe')
        #dir_frame.pack(side = 'top', anchor = 'nw', expand = 1)
        self.dir_frame.focus()

    def entry_get_dir(self):
        """
        Get client specified directory after press Enter.
        """
        path = self.dir_entry.get()
        if not path:
            return
        self.browse_abspath = path
        self.browse_abspath = self.browse_abspath.replace(r'\\\\',os.sep)
        self.browse_abspath = self.browse_abspath.replace(r'\\', os.sep)
        self.browse_abspath = self.browse_abspath.replace(r'/', os.sep)
        #self.dir_entry.delete(0,'end')
        self.update_dir_frame(self.browse_abspath)

    def back_to_parent_folder(self):
        if not self.browse_abspath:
            return
        new_browse_abspath = os.path.dirname(self.browse_abspath)
        if self.browse_abspath != new_browse_abspath:
            self.browse_abspath = new_browse_abspath
            self.update_dir_frame(self.browse_abspath)

    def fit_height(self):
        if self.c.array == '':
            return
        zoom_factor = self.c.zoom_factor * self.c.winfo_height() / float(self.c.photo_image.height())

        if zoom_factor <= self.c.min_zoom_factor:
            zoom_factor = self.c.min_zoom_factor
        if zoom_factor >= self.c.max_zoom_factor:
            zoom_factor = self.c.max_zoom_factor

        self.c.zoom_factor = zoom_factor
        self.c._display()
        self.c._zoom_changed_event_generate()

    def fit_width(self):
        if self.c.array == '':
            return
        zoom_factor = self.c.zoom_factor * self.c.winfo_width() / float(self.c.photo_image.width())

        if zoom_factor <= self.c.min_zoom_factor:
            zoom_factor = self.c.min_zoom_factor
        if zoom_factor >= self.c.max_zoom_factor:
            zoom_factor = self.c.max_zoom_factor

        self.c.zoom_factor = zoom_factor
        self.c._display()
        self.c._zoom_changed_event_generate()

    def fit_window(self):
        if self.c.array == '':
            return
        zoom_factor_width = self.c.zoom_factor * self.c.winfo_width() / float(self.c.photo_image.width())
        zoom_factor_height = self.c.zoom_factor * self.c.winfo_height() / float(self.c.photo_image.height())
        zoom_factor = min(zoom_factor_width, zoom_factor_height)

        if zoom_factor <= self.c.min_zoom_factor:
            zoom_factor = self.c.min_zoom_factor
        if zoom_factor >= self.c.max_zoom_factor:
            zoom_factor = self.c.max_zoom_factor

        self.c.zoom_factor = zoom_factor
        self.c._display()
        self.c._zoom_changed_event_generate()

    def zoom_ori_size(self):
        if self.c.array == '':
            return
        self.c.on_zoom_1()

    def zoom_in(self):
        if self.c.array == '':
            return
        self.c.zoom_factor += 1
        if self.c.zoom_factor > self.c.max_zoom_factor:
            self.c.zoom_factor = self.c.max_zoom_factor
        self.c._display()
        self.c._zoom_changed_event_generate()
        self.status.flash(2000, _('You can drag the left mouse button instead.'))

    def zoom_out(self):
        if self.c.array == '':
            return
        self.c.zoom_factor -= 0.5
        if self.c.zoom_factor < self.c.min_zoom_factor:
            self.c.zoom_factor = self.c.min_zoom_factor
        self.c._display()
        self.c._zoom_changed_event_generate()
        self.status.flash(2000, _('You can drag the left mouse button instead.'))


    def rotate_left_90(self):
        if self.c.array == '':
            return
        self.c.angle += 90

        self.c._display()
        self.c._zoom_changed_event_generate()

    def rotate_right_90(self):
        if self.c.array == '':
            return
        self.c.angle -= 90
        
        self.c._display()
        self.c._zoom_changed_event_generate()

    def rotate_180(self):
        if self.c.array == '':
            return
        self.c.angle += 180
        
        self.c._display()
        self.c._zoom_changed_event_generate()


    def rotate_flip_default(self):
        if self.c.array == '':
            return
        self.c.angle = 0
        self.c.flip_horizontal = False
        self.c.flip_vertical = False
        self.c._display()
        self.c._zoom_changed_event_generate()

    def flip_horizontal(self):
        if self.c.array == '':
            return
        self.c.flip_horizontal = not self.c.flip_horizontal
        self.c._display()
        self.c._zoom_changed_event_generate()

    def flip_vertical(self):
        if self.c.array == '':
            return
        self.c.flip_vertical = not self.c.flip_vertical
        self.c._display()
        self.c._zoom_changed_event_generate()


    ##########################################################
    def _show_icon(self):
        """Show icon in title bar(Windows) or taskbar(Linux)."""
        if 'Windows' == self._platform():
            try:
                if os.path.exists(os.sep.join([os.path.dirname(os.path.abspath(__file__)), 'images', 'icon.ico'])):
                    self.master.iconbitmap(os.sep.join(['images', 'icon.ico']))
            except NameError: # We are the main py2exe script, not a module
                import sys
                
                if os.path.exists(os.sep.join([os.path.dirname(os.path.abspath(sys.argv[0])), 'images', 'icon.ico'])):
                    self.master.iconbitmap(os.sep.join(['images', 'icon.ico']))

        else:
            #Linux.
            try:
                if os.path.exists(os.sep.join([os.path.dirname(os.path.abspath(__file__)), 'images', 'icon.xbm'])):
                    self.master.iconbitmap('@' + os.sep.join(['images', 'icon.xbm']))
            except NameError: # We are the main py2exe script, not a module
                if os.path.exists(os.sep.join([os.path.dirname(os.path.abspath(sys.argv[0])), 'images', 'icon.xbm'])):
                    self.master.iconbitmap('@' + os.sep.join(['images', 'icon.xbm']))

    def _customize_window(self):
        self._show_icon()
        self.master.title(_('title'))
        self.master.geometry(self.settings.get_window_size())
        #zoom maximum window.
        #'''
        if 'Windows' == self._platform():
            self.master.state('zoomed')
        else:
            self.master.wm_attributes("-zoomed", "1")
        #'''
       

    def _bind_events(self):
        self.master.bind_all('<Control-o>', lambda event: self.open_file())
        self.master.bind_all('<Control-p>', lambda event: self.open_series())
        self.master.bind_all('<Control-w>', lambda event: self.close_file_s())
        self.dir_entry.bind("<Return>", lambda event: self.entry_get_dir())


    def main(self):
        """The main GUI."""
        #############################################################
        #three major part: top middle and down.
        self.menuframe = tk.Frame(self.master, bg = 'black')
        self.panedwindow = ttk.PanedWindow(self.master, orient = 'horizontal')
        self.statusframe = tk.Frame(self.master, bg = 'black')

        self.menuframe.pack(side = 'top', fill = 'x')
        self.panedwindow.pack(side = 'top', fill = 'both', expand = 1)
        self.statusframe.pack(side = 'top', fill = 'x')


        #############################################################
        #Deal with status bar:
        self.status = StatusBar(self.statusframe)
        self.status.pack(side = 'left', anchor = 'w')
        #status_seperator=ttk.Separator(statusframe,orient='vertical')
        #status_seperator.pack(fill = 'y')
        #status_seperator.grid(row=0,column=1,sticky='ns')

        #############################################################
        #Deal with menu:
        self.menubar = tk.Menu(self.menuframe)
        self.master.config(menu = self.menubar)
        #-------------------------------------------------------
        def _add_main_menu():
            self.file_menu = tk.Menu(self.menubar, tearoff = 0)#1
            self.edit_menu = tk.Menu(self.menubar, tearoff = 0)#2
            self.view_menu = tk.Menu(self.menubar, tearoff = 0)#3
            self.image_menu = tk.Menu(self.menubar, tearoff = 0)#4
            self.ROI_menu = tk.Menu(self.menubar, tearoff = 0)#5
            self.measure_menu = tk.Menu(self.menubar, tearoff = 0)#6
            self.settings_menu = tk.Menu(self.menubar, tearoff = 0)#7
            self.help_menu = tk.Menu(self.menubar, tearoff = 0)#8

            self.menubar.add_cascade(label = _('m_file'), menu = self.file_menu)#1
            self.menubar.add_cascade(label = _('m_edit'), menu = self.edit_menu)#2
            self.menubar.add_cascade(label = _('m_view'), menu = self.view_menu)#3
            self.menubar.add_cascade(label = _('m_image'), menu = self.image_menu)#4
            self.menubar.add_cascade(label = _('m_ROI'), menu = self.ROI_menu)#5
            self.menubar.add_cascade(label = _('m_measure'), menu = self.measure_menu)#6
            self.menubar.add_cascade(label = _('m_setting'), menu = self.settings_menu)#7
            self.menubar.add_cascade(label = _('m_help'), menu = self.help_menu)#8
        _add_main_menu()
        #-------------------------------------------------------
        def _file_menu():
            self.file_menu.add_command(label = _('m_open_single'), command = self.open_file, accelerator = 'Ctrl+o')
            self.file_menu.add_command(label = _('m_open_series'), command = self.open_series, accelerator = 'Ctrl+p')
            self.file_menu.add_command(label = _('m_close_file_s'), command = self.close_file_s, accelerator = 'Ctrl+w')
            self.file_menu.add_separator()
            self.file_menu.add_command(label = _('m_save_as'), command = self.save_file)
            self.file_menu.add_command(label = _('m_convert_as'), command = self.convert_bmp)
            self.file_menu.add_command(label = _('m_convert_all_as'), command = self.convert_all_bmp)
            self.file_menu.add_separator()
            self.file_menu.add_command(label = _('m_exit'), command = self.SafeExit)
        #-------------------------------------------------------
        def _edit_menu():
            self.edit_menu.add_command(label = _('m_undo'), command = False, state = "disabled")
            self.edit_menu.add_command(label = _('m_redo'), command = False, state = "disabled")
        #-------------------------------------------------------
        def _view_menu():
            self.view_menu.add_command(label = _('tags detail'), command = self.show_tags)


            self.view_tags_menu = tk.Menu(self.view_menu, tearoff = 0)
            self.view_menu.add_cascade(label = _('m_tags'), menu = self.view_tags_menu, state = "disabled")
            self.tag_var1 = tk.BooleanVar()
            self.tag_var1.set(True)
            self.view_tags_menu.add_checkbutton(label = _('m_tag1'), onvalue = True, offvalue = False, variable = self.tag_var1)


            self.view_menu.add_separator()


            self.view_menu.add_command(label = _('m_ori_size'), command = self.zoom_ori_size)
            self.view_menu.add_command(label = _('m_fit_win'), command = self.fit_window)
            self.view_menu.add_command(label = _('m_fit_wid'), command = self.fit_width)
            self.view_menu.add_command(label = _('m_fit_hei'), command = self.fit_height)
            self.view_menu.add_command(label = _('m_zoom_in'), command = self.zoom_in)
            self.view_menu.add_command(label = _('m_zoom_out'), command = self.zoom_out)


            self.view_menu.add_separator()


            self.view_menu.add_command(label = _('m_slide_show'), command = self.slide_show)
        #-------------------------------------------------------
        def _image_menu():
            self.menugif_rotate_180 = tk.PhotoImage(file = os.sep.join(['images', 'turn_180.gif']))
            self.menugif_rotate_left = tk.PhotoImage(file = os.sep.join(['images', 'turn_left.gif']))
            self.menugif_rotate_right = tk.PhotoImage(file = os.sep.join(['images', 'turn_right.gif']))


            self.image_menu.add_command(label = _('m_ro_180'), command = self.rotate_180, image = self.menugif_rotate_180, compound = 'left')
            self.image_menu.add_command(label = _('m_ro_90'), command = self.rotate_left_90, image = self.menugif_rotate_left, compound = 'left')
            self.image_menu.add_command(label = _('m_ro_270'), command = self.rotate_right_90, image = self.menugif_rotate_right, compound = 'left')


            self.image_menu.add_separator()


            self.menugif_filp_hori = tk.PhotoImage(file = os.sep.join(['images', 'flip_hori.gif']))
            self.menugif_filp_vert = tk.PhotoImage(file = os.sep.join(['images', 'flip_vert.gif']))


            self.image_menu.add_command(label = _('m_filp_hori'), command = self.flip_horizontal, image = self.menugif_filp_hori, compound = 'left')
            self.image_menu.add_command(label = _('m_filp_vert'), command = self.flip_vertical, image = self.menugif_filp_vert, compound = 'left')


            self.image_menu.add_separator()


            self.image_menu.add_command(label = _('m_ro_flip_default'), command = self.rotate_flip_default)
        #-------------------------------------------------------
        def _ROI_menu():
            self.ROI_menu.add_command(label = _('m_save_ROIs'), command = self.save_ROI)
            self.ROI_menu.add_command(label = _('m_load_ROIs'), command = self.load_ROI)
        #-------------------------------------------------------
        def _measure_menu():
            self.measure_menu.add_command(label = _('m_distance'), command = self.measure_distance)
            self.measure_menu.add_command(label = _('m_size'), command = False, state = 'disabled')
            self.measure_menu.add_command(label = _('m_stat_in_ROI'), command = False, state = 'disabled')
        #-------------------------------------------------------
        def _setting_menu():
            self.settings_menu.add_cascade(label = _('m_change_language'), menu = self.help_lang_menu)
            self.settings_menu.add_command(label = _('m_set_dir'), command = self.set_dir)
            self.settings_menu.add_command(label = _('m_set_win_size'), command = self.set_win_size)
            self.settings_menu.add_command(label = _('m_set_paned_ratio'), command = self.set_paned_ratio)
            self.settings_menu.add_command(label = _('m_set_sidebar_max_lines'), command = self.set_sidebar_max_lines)
            self.settings_menu.add_command(label = _('m_set_contour_color'), command = self.set_contour_color)
            self.settings_menu.add_command(label = _('m_set_text_color'), command = self.set_text_color)
            
            self.settings_filter_menu = tk.Menu(self.settings_menu, tearoff = 0)
            self.settings_menu.add_cascade(label = _('m_resize_filter_type'), menu = self.settings_filter_menu)
            self.resize_filter_type_int = tk.IntVar()
            self.resize_filter_type_int.set(self.settings.get_resize_filter_type())
            self.settings_filter_menu.add_radiobutton(label = _('m_NEAREST'), command =  self.set_resize_filter_type, variable = self.resize_filter_type_int, value = 0)
            self.settings_filter_menu.add_radiobutton(label = _('m_ANTIALIAS'), command =  self.set_resize_filter_type, variable = self.resize_filter_type_int, value = 1)
            self.settings_filter_menu.add_radiobutton(label = _('m_BILINEAR'), command =  self.set_resize_filter_type, variable = self.resize_filter_type_int, value = 2)
            self.settings_filter_menu.add_radiobutton(label = _('m_BICUBIC'), command =  self.set_resize_filter_type, variable = self.resize_filter_type_int, value = 3)


            self.settings_menu.add_command(label = _('m_set_min_max_zoomfactor'), command = self.set_min_max_zoomfactor)
            self.settings_menu.add_command(label = _('m_backup_ini'), command = self.backup_ini)




        #-------------------------------------------------------
        def _help_menu():
            self.help_lang_menu = tk.Menu(self.help_menu, tearoff = 0)
            self.help_menu.add_cascade(label = 'Change language:', menu = self.help_lang_menu)
            self.lang_var = tk.StringVar()
            self.lang_var.set(self.settings.get_language())
            for i in languages.languages:
                self.help_lang_menu.add_radiobutton(label = i, command = lambda i=i : self.set_lang(i), variable = self.lang_var, value = i)


            self.help_menu.add_command(label = _('m_about'), command = self.help)
            self.help_menu.add_command(label = _('m_contact_author'), command = self.contact)
        #-------------------------------------------------------
        _file_menu()
        _edit_menu()
        _view_menu()
        _image_menu()
        _ROI_menu()
        _measure_menu()
        _help_menu()
        _setting_menu()

        #############################################################
        #Deal with sidebar:
        self.sidebar = tk.Frame(self.panedwindow)
        self.showbox = tk.Frame(self.panedwindow, bg = 'black', name = 'showbox')
        weight_sidebar, weight_showbox = self.settings.get_paned_ratio()
        self.panedwindow.add(self.sidebar, weight = weight_sidebar)
        self.panedwindow.add(self.showbox, weight = weight_showbox)

        #-------------------------------------------------------
        self.dir_back_to_parent_folder_button = tk.Button(self.sidebar, text = '↑', command = self.back_to_parent_folder, relief='groove')
        self.dir_entry = tk.Entry(self.sidebar)
        self.dir_entry_return_button = tk.Button(self.sidebar, text = '↲', command = self.entry_get_dir, relief='groove')#, width = 1
        self.dir_frame = Dir_frame(master = self.sidebar, abspath = self.browse_abspath)


        self.dir_back_to_parent_folder_button.grid(row = 0, column = 0, sticky ='nswe')
        self.dir_entry.grid(row = 0, column = 1, sticky ='nswe')
        self.dir_entry_return_button.grid(row = 0, column = 2, sticky ='nswe')
        self.dir_frame.grid(row = 1, column = 0, columnspan = 3, sticky ='nswe')
        #-------------------------------------------------------
        self.c = Mc.MRI_canvas(self.showbox, bg = 'black', name = 'show_canvas')
        self.c.pack(fill = 'both', expand = 1)

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)

    root.mainloop()


