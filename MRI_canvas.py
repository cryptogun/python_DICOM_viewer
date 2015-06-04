#coding: utf-8
"""
A canvas derived from Tkinter.Canvas for MRI image display
"""
import Tkinter
from PIL import ImageTk, Image
import tkSimpleDialog
import tkMessageBox
class MRI_canvas(Tkinter.Canvas):
    """
    A canvas derived from Tkinter.Canvas
    """
    def __init__(self, parent, *args, **kw):
        Tkinter.Canvas.__init__(self, parent, *args, **kw)
        self.parent = parent
        self.array = ''
        self.z_index = -1
        self.t_index = -1

        #options that can cause different behaviours
        #
        
        #methods for image resize 
        self.resize_filter_type = 0
        #NEAREST = 0
        #ANTIALIAS = 1 # 3-lobed lanczos
        #LINEAR = BILINEAR = 2
        #CUBIC = BICUBIC = 3

        #ROI drawing method
        #  -1 represents free-hand drawing
        #  see below to learn other options
        self.shape_index = -1
        #minimum and maximum zoom factors
        self.min_zoom_factor = .05
        self.max_zoom_factor = 6.

        #ROI drawing methods
        self.object_kinds = [self.create_oval,
                             self.create_rectangle]
        if self.shape_index != -1:
            self.shape = self.object_kinds[self.shape_index]

        self.ROI_color = 'cyan'
        self.multiple_ROIs = True#False

        self.zoom_factor = 1.

        self.angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False


        #contours
        self.contour_coors = {}#{0: [[20, [100, 100, 200, 200, 100, 200]], [30, [300, 300, 400, 400, 400, 300]]]}#real

        self.movable_colors = ('yellow', 'green', self.ROI_color)
        

        self.file_name = ''
        self.seq = None

        
        self.text_coors = {}#{0:[[7, [100, 100], 'hello'], [9, [200, 100], 'world']], 1:[[7, [200, 100], '第二'], [9, [300, 100], '张']]}#real
        self.texts = []#screen
        self._drag_data = {"x": 0, "y": 0, "oid": None}

        self._set_default_windowing()
        self._bind_events()


        self.parent.test = Tkinter.Label(self.parent, text = 'a\n \ntest!!!!!!!\nnew line',bg = 'black', fg = 'white')
        #self.parent.test.pack(in_ = self, anchor = 'se')

        


    def _display(self):
        """
        core of this widget: display one slice of the MRI image array
        """
        #if no data has been loaded
        if self.array == '':
            return
        
        #print(len(self.array.shape), self.z_index, self.t_index, "aaa")
        if len(self.array.shape)==2:
            try:
                self.file_name = self.seq.files[0]
            except AttributeError:# __main__ 'NoneType' object has no attribute 'files'
                pass
            cur_image = self.array.copy()
        elif len(self.array.shape)==3:
            try:
                cur_image = self.array[self.z_index].copy()
            except:
                print "self.z_index = %d (0 - %d)"%(self.z_index, self.array.shape[0]-1)
                if self.z_index > self.array.shape[0]-1:
                    self.z_index = self.array.shape[0]-1
                elif self.z_index < 0:
                    self.z_index = 0
            cur_image = self.array[self.z_index].copy()
            self.file_name = self.seq.files[self.z_index]
        elif len(self.array.shape)==4:
            try:
                cur_image = self.array[self.t_index, self.z_index].copy()
            except:
                print "self.t_index = %d; self.z_index = %d"%(self.t_index, self.z_index)
                if self.t_index > self.array.shape[0]-1:
                    self.t_index = self.array.shape[0]-1
                elif self.t_index < 0:
                    self.t_index = 0
                if self.z_index > self.array.shape[1]-1:
                    self.z_index = self.array.shape[1]-1
                elif self.z_index < 0:
                    self.z_index = 0
                    
                cur_image = self.array[self.t_index, self.z_index].copy()
            self.file_name = self.seq.files[self.t_index+self.z_index*self.array.shape[0]]

        #else, calculate image gray levels according to windowing/leveling setting
        #look up table
        lut_min = 0
        lut_max = 255
        lut_range = lut_max - lut_min

        #current setting
        minv = self.window_center - self.window_width / 2.0
        maxv = self.window_center + self.window_width / 2.0

        #print "window minv = %f, maxv = %f"%(minv, maxv)
        
        #map image gray levels to the display gray levels
        #gray levels less than the minv or greater than the maxv values are set to those values
        min_mask = (minv >= cur_image)
        to_scale = (cur_image > minv) & (cur_image < maxv)
        max_mask = (cur_image >= maxv)

        if min_mask.any(): cur_image[min_mask] = lut_min
        if to_scale.any(): cur_image[to_scale] = ((cur_image[to_scale] - minv) /
                                                  (maxv - minv)) * lut_range + lut_min
        if max_mask.any(): cur_image[max_mask] = lut_max
        
        #convert the image array to a PIL image
        sz = self.array.shape
        im=Image.fromstring('L', (sz[-1], sz[-2]), cur_image.astype('b').tostring())#(sz[-1], sz[-2])
        
        #resize the image if needed
        im=im.resize([int(self.zoom_factor*i+.5) for i in im.size], self.resize_filter_type)
        #rotate an angle if needed.
        im = im.rotate(self.angle)
        if self.flip_horizontal:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if self.flip_vertical:
            im = im.transpose(Image.FLIP_TOP_BOTTOM)

        self.im = im


        #need to store the PhotoImage instance for Tk display purpose
        self.photo_image = ImageTk.PhotoImage(image=self.im)
            


        #enquire the widget size
        actual_width = self.winfo_width()
        actual_height = self.winfo_height()
        canvas_image=self.create_image(actual_width/2., actual_height/2.,
                                       image=self.photo_image, tags = 'image', anchor='center')

        #canvas_patient_info = self.create_image(actual_width/2., actual_height/2., image=self.photo_image, anchor='center')

        self.tag_lower('image')

        imx,imy = self.photo_image.width(), self.photo_image.height()
        self['scrollregion']=(min(0,(actual_width-imx)/2),min(0,(actual_height-imy)/2),max((actual_width+imx)/2,actual_width),max((actual_height+imy)/2,actual_height))

        #if there is an ROI

        #if there are contours
        self._display_details()
        self._display_contours()
        self._display_text()
        #to force update the screen
        #using self.update() may cause looping
        self.update_idletasks()

        #self.update()


    def _display_details(self):
        return
        for oid in self.find_withtag('details'):
            self.delete(oid)
        scrollregion = [int(i) for i in self['scrollregion'].split(' ')]
        #print(self['scrollregion'][2], self['scrollregion'][0])

        wx = self.canvasx((scrollregion[2]-scrollregion[0])*sum(self.parent.cxsb.get())/2.0)
        wy = self.canvasy((scrollregion[3]-scrollregion[1])*sum(self.parent.cysb.get())/2.0)
        #print(wx,wy)
        self.create_text(wx, wy, text = self.seq.patient.name, tags = 'details', fill = 'blue')
        #print('cysb',,sum(self.parent.cysb.get())/2.0)
        #self.tag_raise('details')
        #self.focus_set()


    def _display_text(self):
        for oid in self.find_withtag('text'):
            self.delete(oid)

        if not (self.z_index in self.text_coors):
            return

        for i in self.text_coors[self.z_index]:
            screen_coors = self._map_coordinates(i[1], screen_to_image = False)
            i[0] = self.create_text(screen_coors, text = i[2], tags = 'text', font = ('TimesNewRoman', 12), fill = 'green', anchor = 'nw')
        self.tag_raise('text')

    def _create_text(self, event):
        text = tkSimpleDialog.askstring('Enter text:','')
        if text == None: return
        has_character = False
        for i in text:
            if i != ' ':
                has_character = True
                break
        if has_character:
            cx = self.canvasx(event.x)
            cy = self.canvasy(event.y)
            oid = self.create_text(cx, cy, text = text, tags = 'text', font = ('TimesNewRoman', 12), fill = 'green', anchor = 'nw')
            #self._save text coors
            if not (self.z_index in self.text_coors):
                self.text_coors.update({self.z_index: []})
            z_text = self.text_coors[self.z_index]
            real_coors = self._map_coordinates(self.coords(oid))
            z_text.append([oid, real_coors, text])
            self.text_coors.update({self.z_index: z_text})

    def _change_text(self, event):
        if self.type('current') != "text":
            return
        
        cx = self.canvasx(event.x)
        cy = self.canvasy(event.y)
        oid = self.find_closest(cx, cy, halo = 4)[0]
        text = tkSimpleDialog.askstring('Edit text:', '', initialvalue = self.itemcget(oid, 'text'))
        
        if text == None: return

        has_character = False
        for i in text:
            if i != ' ':
                has_character = True
                break
        if has_character:
            self.itemconfig(oid, text = text)
            z_text = self.text_coors[self.z_index]
            for i in z_text:
                if i[0] == oid:
                    i[2] = text
                    break
            self.text_coors.update({self.z_index: z_text})
        else:
            self.delete(oid)
            z_text = self.text_coors[self.z_index]
            for index in range(len(z_text)):
                if z_text[index][0] == oid:
                    del z_text[index]
                    break
            self.text_coors.update({self.z_index: z_text})
            if z_text == []:
                del self.text_coors[self.z_index]

        #self._save_text _coors()


    def _display_contours(self):
        """
        redraw all contours
        """
        #first remove existing contours
        for oid in self.find_withtag('polygon'):
            self.delete(oid)
        '''
        if len(self.contours) > 0:
            #different colors represent different types of contours
            for color in self.contours.keys():
                #for each contour type, there are contours on different slices
                for slicen in self.contours[color].keys():
                    self.delete(self.contours[color][slicen])
                self.contours.pop(color)
        '''
        if not (self.z_index in self.contour_coors):
            return

        if self.contour_coors[self.z_index] == []:
            del self.contour_coors[self.z_index]
        if self.contour_coors == {}:
            return
        for z_each_contour in self.contour_coors[self.z_index]:
            coors = self._coor_to_screen(z_each_contour[1])
            z_each_contour[0] = self.create_polygon(coors,fill="",outline='cyan', tags = 'polygon')
        self.tag_raise('text')
        
    def set_array(self, array):
        """
        set the image data to be displayed.
        Input:
            array: can be 2-, 3-, and 4-dimensional scipy array
        """
        self.array = array
        self._set_default_windowing()

        #use the same z_index value unless it is out of bound
        if len(self.array.shape)==3:
            if self.z_index < 0:
                self.z_index = 0
            elif self.z_index > self.array.shape[-3] - 1:
                self.z_index = self.array.shape[-3] - 1
        elif len(self.array.shape)==4:
            if self.z_index < 0:
                self.z_index = 0
            elif self.z_index > self.array.shape[-3] - 1:
                self.z_index = self.array.shape[-3] - 1
            #check the extra dimension
            if self.t_index == -1:
                self.t_index = 0
            elif self.t_index > self.array.shape[-4] - 1:
                self.t_index = self.array.shape[-4] - 1

        #print "z_index = %d; t_index = %d"%(self.z_index, self.t_index)
        self._display()
        self._slice_change_event_generate()

    '''
    def set_contours(self, contour_coors, to_the_slice=True):
        """
        set a set of contours
        """
        self.contour_coors = contour_coors
        if to_the_slice:
            self.z_index = self.contour_coors.values()[0].keys()[0]
        self._display()
    '''
    def clear_contours(self):
        self.contour_coors = {}
        self._display()

    def _set_default_windowing(self):
        if self.array == '':
            self.window_center = None
            self.window_width = None
            return
        maxv = self.array.max()
        minv = self.array.min()
        self.window_center = (maxv / 2.0) + (minv / 2.0)
        #self.window_width = maxv - minv + 1.0
        self.window_width = maxv - minv
        #print "in _set_default_windowing: max=%f, min=%f, wc=%f, ww=%f"%(maxv,minv,self.window_center,self.window_width)
        
    #######################################
    #event generating and binding
    def _slice_change_event_generate(self):
        """
        create a custom event that indicates the displayed image slice is changed.
        a custom event <<Slice_Changed>> will be created after this function is returned.
        """
        self.event_generate("<<Slice_Changed>>",when='tail')
    def _ROI_drawn_event_generate(self):
        self.event_generate("<<ROI_Drawn>>",when='tail')
    def _zoom_changed_event_generate(self):
        self.event_generate("<<Zoom_Changed>>",when='tail')
    def generate_button45_on_windows(self, event):
        scroll_line = int(event.delta / 120)
        if scroll_line in (1, 2, 3, 4):
           self.event_generate("<Button-4>", x = event.x, y = event.y)
        elif scroll_line > 4:
            for i in range(scroll_line - 3):
                self.event_generate("<Button-4>", x = event.x, y = event.y)
        elif scroll_line in (-1, -2, -3, -4):
            self.event_generate("<Button-5>", x = event.x, y = event.y)
        elif scroll_line < -4:
            for i in range(-scroll_line - 3):
                self.event_generate("<Button-5>", x = event.x, y = event.y)


    def OnTextButtonPress(self, event):
        '''Being drag of an object'''
        # record the item and its location
        cx = self.canvasx(event.x)
        cy = self.canvasy(event.y)
        self._drag_data["oid"] = self.find_closest(cx, cy, halo = 4)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def OnTextMotion(self, event):
        '''Handle dragging of an object'''
        # compute how much this object has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # move the object the appropriate amount
        self.move(self._drag_data["oid"], delta_x, delta_y)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def OnTextButtonRelease(self, event):
        '''End drag of an object'''
        #self.OnTextMotion(event)
        # reset the drag information
        oid = self._drag_data["oid"]
        self._drag_data["oid"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        #self._save_text _coors()
        z_text = self.text_coors[self.z_index]
        for i in z_text:
            if i[0] == oid:
                i[1] = self._map_coordinates(self.coords(oid))
                break
        self.text_coors.update({self.z_index: z_text})


    def _bind_events(self):
        """
        bind events that will be handled by this class, including
        mouse wheel forward  -> change z-axis or time location
        mouse wheel backward -> change z-axis or time location
        mouse right button pressed and moved -> windowing and leveling
        mouse  left button pressed and moved -> zooming
        widget is resized -> redraw canvas
        """
        self.bind('<Shift-ButtonPress-1>', self._create_text)

        self.bind("<MouseWheel>", self.generate_button45_on_windows)
        self.bind("<Button-4>", self.on_wheel_forward) #wheel forward
        self.bind("<Button-5>", self.on_wheel_backward) #wheel backward

        #ROI drawing using left mouse button and Control key
        self.bind("<Control-ButtonPress-1>", self.on_ROI_starting)
        self.bind("<Control-B1-Motion>", self.on_ROI_growing)
        self.bind("<Control-ButtonRelease-1>", self.on_ROI_ending)
        
        #zooming or moving ROI (while captured) using left mouse button
        self.bind("<ButtonPress-1>", self.on_mouse_left_down)
        self.bind("<B1-Motion>", self.on_mouse_left_down_moving)
        self.bind("<ButtonRelease-1>", self.on_mouse_left_up)
        self.bind("<Double-1>", self.on_zoom_1)
        
        #changing windowing and leveling set using right mouse button
        self.bind("<ButtonPress-3>", self.on_window_level_starting)
        self.bind("<B3-Motion>", self.on_window_level_changing)
        self.bind("<ButtonRelease-3>", self.on_window_level_ending)
        self.bind("<Double-3>", self.on_default_window_level)

        self.bind("<Configure>", self.on_configure)

        self.bind("<ButtonPress-2>", self.button2_press)
        self.bind("<B2-Motion>", self.button2_moving)
        self.bind("<ButtonRelease-2>", self.button2_release)
        #self.bind("<<Zoom_Changed>>", self._zoom_changed)
    #event generating and binding end
    #######################################


    #######################################
    #coordinates transferring
    def _map_coordinates(self, coors, screen_to_image = True):
        if screen_to_image:
            _from_sz = [self.winfo_width(), self.winfo_height()]
            _to_sz = [self.array.shape[-1], self.array.shape[-2]]
            factor = 1./self.zoom_factor
        else:
            _to_sz = [self.winfo_width(), self.winfo_height()]
            _from_sz = [self.array.shape[-1], self.array.shape[-2]]
            factor = self.zoom_factor
        n = len(coors)/2
        #print n, coors,self.can_sz_x, self.image_size[-1]
        re_coors = []
        #print coors
        for i in range(n):
            x = (coors[i*2] - _from_sz[0]/2.0) * factor + _to_sz[0]/2.0
            y = (coors[i*2+1] -_from_sz[1] /2.0) * factor + _to_sz[1]/2.0
            re_coors.append(int(x+.5))
            re_coors.append(int(y+.5))
        return re_coors
    def _coor_to_image(self,*coors):
        return self._map_coordinates(coors, screen_to_image = True)
    def _coor_to_screen(self, coors):
        return self._map_coordinates(coors, screen_to_image = False)
    #coordinates transferring end
    #######################################


    #enable to move ROI
    def on_mouse_left_down(self, event):
        if self.array == '':
            return
        #print('current',self.type('current'))
        #if self.type('current') == "text":
        #    self.OnTextButtonPress(event)
        #else:
        
        self.focus_set()
        #get canvas coordinates
        cx = self.canvasx(event.x)
        cy = self.canvasy(event.y)
        #print "canvas coordinates = (%d, %d"%(cx, cy)
        oid = self.find_closest(cx, cy, halo = 4)[0]
        '''
        if self.text_coors.has_key(self.z_index):
            z_text = self.text_coors[self.z_index]
            for i in z_text:
                if i[0] == oid:
                    self.text_grabbed = True
                    self.OnTextButtonPress(event)
                    return
        '''

        
        for a in range(1):
            #grab text
            if self.text_coors.has_key(self.z_index) and oid in (each_text_coors[0] for each_text_coors in self.text_coors[self.z_index]):
                self.text_grabbed = True
                self.OnTextButtonPress(event)
                break
        else:
            #grab contour
            #print "oid = %s"%oid
            #pprint.pprint(self.contours)
            #print self.contours['red'].values()
            #print oid in self.contours['red'].values()
            if self.contour_coors.has_key(self.z_index) and \
            oid in (each_contour[0] for each_contour in self.contour_coors[self.z_index]):
                #print "oid(%s) is a contour!"%oid
                self.ROI_grabbed = True
                self.grab_ROI(event)
                #break
            else:
                #grab image, zooming.
                self.zoom_started = True
                self.zoom_starting(event)

    def on_mouse_left_down_moving(self, event):
        if hasattr(self, 'text_grabbed'):
            self.OnTextMotion(event)
        else:
            if hasattr(self, "ROI_grabbed"):
                self.move_contour(event)
            elif hasattr(self, "zoom_started"):
                self.zoom_changing(event)
            else:
                pass
    def on_mouse_left_up(self, event):
        if hasattr(self, 'text_grabbed'):
            self.OnTextButtonRelease(event)
            del self.text_grabbed
        else:
            if hasattr(self, "ROI_grabbed"):
                self.drop_contour(event)
                del self.ROI_grabbed
            elif hasattr(self, "zoom_started"):
                self.zoom_ending(event)
                del self.zoom_started
            else:
                pass
        

    #######################################
    #contours and contour moving
    def grab_ROI(self, event):
        #self.config(cursor='hand1')
        if self.array == '':
            return
        self.grabbed = True

        cx = self.canvasx(event.x)
        cy = self.canvasy(event.y)
        obj = self.find_closest(cx, cy, halo = 4)[0]

        self.old_z = self.z_index
        self._drag_data['oid'] = obj
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y
    def move_contour(self, event):
        if hasattr(self, 'grabbed') and self.grabbed:
            offset_x = event.x - self._drag_data['x']
            offset_y = event.y - self._drag_data['y']
            
            self.move(self._drag_data["oid"], offset_x, offset_y)
            self._drag_data['x'] = event.x
            self._drag_data['y'] = event.y
            
    def drop_contour(self, event):
        if hasattr(self, 'grabbed') and self.grabbed:
            self.move_contour(event)

            z_contours = self.contour_coors[self.old_z]
            for z_each_contour in z_contours:
                if z_each_contour[0] == self._drag_data["oid"]:

                    z_each_contour[1] = self._map_coordinates(self.coords(self._drag_data["oid"]))
                    break
            if z_contours != []:
                self.contour_coors.update({self.old_z: z_contours})

            self._drag_data["oid"] = None
            self._drag_data["x"] = 0
            self._drag_data["y"] = 0
            del self.grabbed
            del self.old_z



    #contours and ROI moving end
    #######################################

    
    #######################################
    #zoom in and out
    #
    def zoom_starting(self, event):
        #if no data array is avaible, do not bother
        if self.array == '':
            return
        self.start = event
        self.old_zoom_factor = self.zoom_factor
        
    def zoom_changing(self, event):
        if not hasattr(self, 'start'):
            return
        offy = self.start.y - float(event.y)
        self.zoom_factor = self.old_zoom_factor + float(offy)/100
        '''
        #self.zoom_factor += sqrt(abs(offy))/100 * (offy/abs(offy))
        if offy > 0:
            #self.zoom_factor = self.old_zoom_factor * (1+float(offy)/200)
            #self.zoom_factor += float(offy)/self.photo_image.height() *2
        else:
            if offy != 0:
                #self.zoom_factor += float(offy)/self.photo_image.height() *2
                #self.zoom_factor = self.old_zoom_factor / (1 - float(offy)/200)
        '''
        if self.zoom_factor <= self.min_zoom_factor:
            self.zoom_factor = self.min_zoom_factor
        if self.zoom_factor >= self.max_zoom_factor:
            self.zoom_factor = self.max_zoom_factor
            
        self._display()
        self._zoom_changed_event_generate()
    def zoom_ending(self, event):
        """
        clean variables that used for zooming
        """
        if hasattr(self, 'start'):
            del self.start
            del self.old_zoom_factor
    def on_zoom_1(self, event = None):
        self.zoom_factor = 1.
        self._display()
        self._zoom_changed_event_generate()
    #zoom in and out end
    #######################################

    '''
    #######################################
    #ROI generating
    #
    #update 09/26/2012
    #I add a free-hand drawing option
    #  when self.shape is set to be -1
    #  this option is procecced separately from other two options
    #
    #  except some of the below functions are changed,       # this turns out
    #  I also add two more lines in self._dispay() funcation # to be unnecessary
    #

    def _create_ROI(self, *coors):
        if coors != ():
            if self.shape_index == -1:
                self.ROI_drawn = self.create_polygon(coors, fill='',outline=self.ROI_color, tags = 'polygon')
            else:
                self.ROI_drawn = self.shape(*coors, outline=self.ROI_color)
    '''

    def _right_click_delete_ROI(self, event):
        if self.type('current') != "polygon":
            return
        
        cx = self.canvasx(event.x)
        cy = self.canvasy(event.y)
        oid = self.find_closest(cx, cy, halo = 4)[0]
        if oid:            
            delete = tkMessageBox.askyesno(title='Delete ROI', message='Sure to delete this circle?')
            if delete:
                for i in range(len(self.contour_coors[self.z_index])):
                    if self.contour_coors[self.z_index][i][0] == oid:
                        break
                del self.contour_coors[self.z_index][i]
                self._display_contours()


    def on_ROI_starting(self, event):
        if self.array == '':
            return
        self.focus_set()
        self.start = event
        self.freehand_coors = [self.canvasx(event.x), self.canvasy(event.y)]
    def on_ROI_growing(self, event):
        if not hasattr(self, 'start'):
            return
        #free-hand drawing
        if self.shape_index == -1:
            self.create_line(self.canvasx(self.start.x),
                                              self.canvasy(self.start.y),
                                              self.canvasx(event.x),
                                              self.canvasy(event.y),
                                              fill = 'cyan',
                                              tag='line')
            self.start = event
            self.freehand_coors.append(self.canvasx(event.x))
            self.freehand_coors.append(self.canvasy(event.y))
            return
        '''
        #self._create_ROI(self.canvasx(self.start.x),
                                              self.canvasy(self.start.y),
                                              self.canvasx(event.x),
                                              self.canvasy(event.y))
        '''
    def on_ROI_ending(self, event):
        #self._extract_array_ROI_data()
        self._ROI_drawn_event_generate()
        if self.shape_index == -1:
            for item in self.find_withtag('line'):
                self.delete(item)
            #new_ROI_coors = self._coor_to_image(*self.freehand_coors)
            #print self.freehand_coors
            #print self.ROI_coors

            self.freehand_coors.append(self.canvasx(event.x))
            self.freehand_coors.append(self.canvasy(event.y))
            #add it to contours
            oid = self.create_polygon(self.freehand_coors,fill="",outline='cyan', tags = 'polygon')
            #print([oid, new_ROI_coors])
            if not self.z_index in self.contour_coors:
                self.contour_coors[self.z_index] = []
            self.contour_coors[self.z_index].append([oid, self._coor_to_image(*self.freehand_coors)])


            self._display_contours()
            return

    #ROI generating end
    #######################################

    
    #######################################
    #windowing and leveling
    def on_window_level_starting(self, event):
        if self.array == '':
            return

        self._change_text(event)
        self._right_click_delete_ROI(event)
        self.start = event
        self.old_wc = self.window_center
        self.old_ww = self.window_width
        self.range_factor = float(self.array.max() - self.array.min())/4000.
    def on_window_level_changing(self, event):
        if not hasattr(self, 'start'):
            return
        offx = float(event.x) - self.start.x
        offy = float(event.y) - self.start.y
        #print offx, offy
        #data_range = 1000
        
        self.window_center = self.old_wc+float(offx)*self.range_factor
        self.window_width = self.old_ww+float(offy)*self.range_factor*2
        self._display()
    def on_window_level_ending(self, event):
        #clean up
        if hasattr(self, 'start'):
            del self.start
            del self.old_wc
            del self.old_ww
            del self.range_factor
    def on_default_window_level(self, event):
        self._set_default_windowing()
        self._display()
    #windowing and leveling end
    #######################################
    
    def on_configure(self, event):
        #if the widget is resized
        #redraw the image
        self._display()
    def on_wheel_backward(self,event):
        self._scroll_slice(event, down=False)
    def on_wheel_forward(self, event):
        self._scroll_slice(event, down=True)
    def _scroll_slice(self, event, down=True):
        if self.array == '':
            return
        #print(len(self.array.shape))
        if len(self.array.shape) == 2:
            return
        elif len(self.array.shape) == 3:
            self._scroll(z=True, down = down)
        elif len(self.array.shape) == 4:
            x = event.x
            #y = event.y
            ww = self.winfo_width()
            #print(x, ww, 'width') 
            #wh = self.winfo_height()
            if x < ww/2.:
                self._scroll(z=True, down=down)
            else:
                self._scroll(z=False, down=down)

    def _scroll(self, z=True, down=True):
        change = True
        #print(z,'z or t')
        if z:
            if down:
                if self.z_index > 0:
                    self.z_index -= 1
                else:
                    change = False
            else:
                if self.z_index < self.array.shape[-3]-1:
                    self.z_index += 1
                else:
                    change = False
        else:
            if down:
                if self.t_index > 0:
                    self.t_index -= 1
                else:
                    change = False
            else:
                if self.t_index < self.array.shape[-4]-1:
                    self.t_index += 1
                else:
                    change = False
        if change:
            self._display()
            self._slice_change_event_generate()


    def button2_press(self, event):
        if self.array == '':
            return
        self.measure_event = event
        self.pointa = self._coor_to_image(self.canvasx(event.x), self.canvasy(event.y))

    def button2_moving(self, event):
        if self.array == '':
            return
        pass
        for oid in self.find_withtag('templine'):
            self.delete(oid)
        self.create_line(self.canvasx(self.measure_event.x), self.canvasy(self.measure_event.y), self.canvasx(event.x), self.canvasy(event.y), fill = 'green', tags = 'templine')

    def button2_release(self, event):
        if self.array == '':
            return
        for oid in self.find_withtag('templine'):
            self.delete(oid)
        measure_line = self.create_line(self.canvasx(self.measure_event.x), self.canvasy(self.measure_event.y), self.canvasx(event.x), self.canvasy(event.y), fill = 'green', tags = 'finalline')
        self.pointb = self._coor_to_image(self.canvasx(event.x), self.canvasy(event.y))
        import dicom
        f = dicom.read_file(self.file_name, stop_before_pixels=True)
        spacing_xy = f[0x0028, 0x0030].value
        if (self.angle / 90 % 2):
            #if True, by _coor_to_image pointa and pointb were wrong. Todo: rotate polygon and text.
            spacing_xy = spacing_xy[::-1]
            #and wrong again manualy, wrong x wrong = right.
            
        import numpy
        self.distance = numpy.sqrt(((self.pointa[0]-self.pointb[0])*spacing_xy[0])**2+((self.pointa[1]-self.pointb[1])*spacing_xy[1])**2)

        measure_text = self.create_text(self.canvasx(event.x)+10, self.canvasy(event.y)+10, text = str('%.2f' %self.distance)+'mm', fill = 'red', tags = 'finalline')
        def vanish():
            for oid in self.find_withtag('finalline'):
                self.delete(oid)
        self.after(5000, vanish)

        del self.measure_event









if __name__ == "__main__":
    import dicom
    import tkFileDialog
    import sys


    main = Tkinter.Tk()
    main.protocol('WM_DELETE_WINDOW', lambda: main.destroy() or sys.exit()) 

    c = MRI_canvas(main, bg='black')
    c.pack(fill='both', expand=1)
    
    def add_array():
        path=tkFileDialog.askopenfilename()
        if path!='':
            try:
                df=dicom.read_file(path)
                c.set_array(df.pixel_array)

            except dicom.filereader.InvalidDicomError:
                pass

        
    def del_contour():
        c.clear_contours()

    Tkinter.Button(main, text = "add array", command=add_array).pack()
    Tkinter.Button(main, text = "remove contour", command=del_contour).pack()

    main.mainloop()
