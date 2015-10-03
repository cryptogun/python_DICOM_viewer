# -*- coding: utf-8 -*-
import ConfigParser#read and save configure.


class Settings:
    """
    Read configure info from settings.ini.
    """
    def __init__(self):
        self._read_ini()

    def _read_ini(self):
        """ Read settings.ini """
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
        """Get interface language saved in ini file."""
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
        	# create section if None.
            if not self.config.has_section('Languages'):
                self.config.add_section('Languages')
            self.config.set('Languages', 'language', string.encode('utf-8'))
            self.config.write(configfile)

    def get_directory(self):
        """Get initial directory to parse."""
        try:
            return self.config.get('Initial Directory', 'directory')
        except:
            #if not found, parse root instead.
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
        Get window size in ini file.
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
        Get ratio of navi window and disp window from ini file.
        """
        try:
            string = self.config.get('Paned Windows Ratio', 'ratio').replace('：', ':')
            return map(int, string.split(':'))
        except:
            return (1, 6)



    def set_paned_ratio(self, string):
        """
        Set paned retio to ini file.
        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Paned Windows Ratio'):
                self.config.add_section('Paned Windows Ratio')
            self.config.set('Paned Windows Ratio', 'ratio', string.encode('utf-8'))
            self.config.write(configfile)


    def get_sidebar_max_lines(self):
        """
        Get number of lines to show in navi window.
        """
        try:
            return int(self.config.get('Sidebar Max Lines', 'lines'))
        except:
            return 29


    def set_sidebar_max_lines(self, string):
        """
        Customize sidebar lines and save in file.
        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Sidebar Max Lines'):
                self.config.add_section('Sidebar Max Lines')
            self.config.set('Sidebar Max Lines', 'lines', string.encode('utf-8'))
            self.config.write(configfile)

    def get_resize_filter_type(self):
        """
        Get resize filter type eg.
            #NEAREST = 0
            #ANTIALIAS = 1 # 3-lobed lanczos
            #LINEAR = BILINEAR = 2
            #CUBIC = BICUBIC = 3
        """
        try:
            type_int = int(self.config.get('Resize Filter Type', 'type'))
            if type_int in (0, 1, 2, 3):
                return type_int
            else:
                #if not 0,1,2,3
                return 0
        except:
            #if not exist in ini file:
            return 0

    def set_resize_filter_type(self, string):
        """

        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Resize Filter Type'):
                self.config.add_section('Resize Filter Type')
            self.config.set('Resize Filter Type', 'type', string.encode('utf-8'))
            self.config.write(configfile)





    def get_min_max_zoomfactor(self):
        """

        """
        try:
            min_max = self.config.get('Min Max Zoom Factor', 'min max').split(' ')
            min_max = [float(i) for i in min_max]
            return min_max
        except:
            return [0.05, 6.0]


    def set_min_max_zoomfactor(self, string):
        """

        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Min Max Zoom Factor'):
                self.config.add_section('Min Max Zoom Factor')
            self.config.set('Min Max Zoom Factor', 'min max', string.encode('utf-8'))
            self.config.write(configfile)



    def get_contour_color(self):
        """

        """
        try:
            return self.config.get('Colors', 'contour color')
        except:
            return 'cyan'


    def set_contour_color(self, string):
        """

        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Colors'):
                self.config.add_section('Colors')
            self.config.set('Colors', 'contour color', string.encode('utf-8'))
            self.config.write(configfile)


    def get_text_color(self):
        """

        """
        try:
            color = self.config.get('Colors', 'text color')
            if color.startswith('#'):
                return color
            else:
                return 'green'
        except:
            return 'green'


    def set_text_color(self, string):
        """

        """
        string = string.decode('utf-8')
        with open('settings.ini', 'w') as configfile:
            if not self.config.has_section('Colors'):
                self.config.add_section('Colors')
            self.config.set('Colors', 'text color', string.encode('utf-8'))
            self.config.write(configfile)
