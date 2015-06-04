#MR sequence class
#
#generate an MR sequence instance that extract information
#from the dicom headers and the MR data
#
#to do
#current initialization requires a directory name
#however, when multiple sequences mixed in the same directory
#this program will fail
#need to provide additional way to specify a sequence
#such as a list of files
import os
import numpy as scipy
import dicom
from operator import itemgetter
from MRI_slice import MRI_slice

#DOD_path = "D:\\pydicom viewer\\pydicom\\anonymized_data_08272014\\000000\\401"

class MRI_sequence:
    def __init__(self, directory, files=None):
        self.files = files
        self.directory = directory
        self.get_dicom_files()
        self.get_modality()
        if self.modality != "MR":
            #print "Sequence %s is not a MR sequence, %s instead"%(self, self.modality)
            self.is_MRI_sequence = False
            self.get_patient()
            self.get_series_number()
            self.get_scanner()
            self.get_scan_date_time()
            self.get_scan_description()
            self.sequence_type=self.determine_sequence_type()
        else:
            #some screen capture also set modality "MR"!
            if self.directory.split('/')[-1][:2] == 'SC':
                """
                print "Please make sure this directory containing a MR sequence!"
                print self
                print "If it is please modify the directory name to 'MR'!"
                """
                self.is_MRI_sequence = False
                return
            self.get_patient()
            self.get_series_number()
            self.get_scanner()
            self.get_scan_date_time()
            self.get_scan_description()
            self.is_MRI_sequence = True
            self.sequence_type=self.determine_sequence_type()
    def get_sequence_type(self):
        """
        return what sequence this is, either
        T2 (also including orientation, T2_TRA, T2_SAG, T2_COR)
        T1
        DW
        DCE
        and others
        """
        if hasattr(self, 'seqtype'):
            return self.seqtype
        else:
            return self.determine_sequence_type()
    def set_sequence_type(self, seqtype):
        """
        assign the sequence to a certain type
        """
        self.sequence_type = seqtype
    def _create_cross_ref_table_for_instance_slice_numbers(self, keys):
        """
        locations = []
        instance_numbers = []
        file_indices = []
        for i,f in enumerate(self.files):
            slc = MRI_slice(f)
            locations.append(slc.get_tag_value("SliceLocation"))
            instance_numbers.append(slc.get_tag_value("InstanceNumber"))
            file_indices.append(i)
        inds = scipy.argsort(locations)
        #print inds
        self.slicen_by_instance_number = dict(zip(instance_numbers, inds))
        self.instancen_by_slice_number = dict(zip(inds, instance_numbers))
        self.filen_by_slice_number = dict(zip(file_indices, inds))
        #print self.slicen_by_instance_number
        """
        #self._get_pixel_array_4D(skip_pixel_array=True)
        
        #get RANKED file number, extra dimension indices, locations, and instance number
        ind, t, z, instancens = zip(*keys)
        
        slicen = map(z.index, z)
        #dict from instance number to slice number
        self.slicen_by_instance_number = dict(zip(instancens,slicen))
        
        #get the length of the two dimensions
        n_t = len(set(t))
        n_z = len(set(z))
        if n_t == 1:
            self.instancen_by_slice_number = dict(zip(slicen,instancens))
            self.filen_by_slice_number = dict(zip(slicen,ind))
        else:
            #print keys

            #print self.slicen_by_instance_number
            #dict from slice number to instance number
            #  the dict values are lists of instance numbers
            self.instancen_by_slice_number = {}
            for sn,isn in zip(slicen, instancens):
                if not self.instancen_by_slice_number.has_key(sn):
                    self.instancen_by_slice_number[sn] = [isn]
                else:
                    self.instancen_by_slice_number[sn].append(isn)
            #print self.instancen_by_slice_number
            #dict from slice number to file number
            #  similarly, the dict values are lists of file numbers
            self.filen_by_slice_number = {}
            for sn,isn in zip(slicen, ind):
                if not self.filen_by_slice_number.has_key(sn):
                    self.filen_by_slice_number[sn] = [isn]
                else:
                    self.filen_by_slice_number[sn].append(isn)
            #print self.filen_by_slice_number

    def get_slicen_from_instance_number(self, instance_number):
        return self.slicen_by_instance_number[instance_number]
    def get_instance_from_slice_number(self, slice_number):
        return self.instancen_by_slice_number[slice_number]
    def get_filen_from_slice_number(self, slice_number):
        return self.filen_by_slice_number[slice_number]
    def read_data(self):
        """
        override this function if needed
        """
        """
        self._create_cross_ref_table_for_instance_slice_numbers()
        data = []
        locations = []
        for f in self.files:
            slc = MRI_slice(f)
            data.append(slc.get_pixel_array())
            locations.append(slc.get_tag_value("SliceLocation"))
        data = scipy.array(data)
        #print locations
        inds = scipy.argsort(locations)
        #print inds
        data = data[inds]
        self.data = data
        """
        is_4D, data, keys = self._get_pixel_array_4D(skip_pixel_array=False)
        self.data = data

    def merge_with(self, other):
        self.files.extend(other.files)
        self.the_other_sequence = other
        
    def _save_dicom_volume(self, dicoms, output_path):
        import shutil
        for dicom in dicoms:
            dst = os.path.join(output_path, os.path.basename(dicom))
            print "copy from %s to %s"%(dicom, dst)
            shutil.copyfile(dicom, dst)
    def _get_all_dicom_key_values(self):
        tag_dict = {}
        for f in self.files:
            dcm = dicom.ReadFile(f, stop_before_pixels=True,force=True)
            for key in dcm.dir():
                value = getattr(dcm,key,None)
                if tag_dict.has_key(key):
                    if value not in tag_dict[key]:
                        tag_dict[key].append(value)
                else:
                    tag_dict[key] = [value]
        multiple_values, identical_value = {},{}             
        for key in tag_dict.keys():
            if len(tag_dict[key]) != 1:
                multiple_values[key] = tag_dict[key]
            else:
                identical_value[key] = tag_dict[key][0]
        return identical_value, multiple_values

    def _get_pixel_array_4D(self, is_DCE_sequence=True, skip_pixel_array=False):
        self.DCE_seq = is_DCE_sequence
        self.is_4D = True
        def _get_space_key(slc):
            return slc.get_tag_value("SliceLocation")
        def _get_extra_dim_key(slc):
            """
            if is_DCE_sequence:
                #for DCE sequence
                # using time point as the second sort index
                return slc.get_tag_value("TemporalPositionIdentifier")
            else:
                #for DWI sequence
                # using b-value as the second sort index
                if 'GE' in self.scanner.manufacturer:
                    return slc.get_tag_value((0x43,0x1039))[0]
                else:
                    #return slc.get_tag_value((0x18,0x9087))
                    return slc.get_tag_value((0x2001,0x1003))
                    #other possible keys
                    #b.append(sl.get_tag_value((0x2001,0x1003)))
                    #other possible tags
                    #dcm.get_tagvalue((0x2005,0x140f))[0][0x18,0x9087].value
                    #dcm.get_tagvalue((0x18,0x9087))
            """
            if self.is_4D:
                if self.DCE_seq:
                    v = slc.get_tag_value("TemporalPositionIdentifier")
                else:

                    # what is this?



                    if 'GE' in self.scanner.manufacturer:
                        v = slc.get_tag_value((0x43,0x1039))[0]
                        '''From: http://goozhong.blogspot.com/2012/05/dti-information-in-dicom-file.html
                        DTI information include B-value, 3 gradient value of each direction. But these information is not the standard information for DICOM file, so different company store these information in different parts.
                        For GE data:
                        (0x0043,0x1039) b value
                        For Siemens data:
                        (0x0019,0x100c) b value

                        '''
                    else:
                        v = slc.get_tag_value((0x2001,0x1003))#PMS_Diffusion_B_Factor/philips_bvalue_tag/Diffusion_B-Factor. From google search.
                        try:
                            float(v)
                        except:
                            v = slc.get_tag_value((0x18,0x9087))#Diffusion b-value. From RadiAnt.
                #print v
                if v == None:
                    #flip the flag if no value is available
                    self.DCE_seq = not self.DCE_seq

                    if self.DCE_seq:
                        v = slc.get_tag_value("TemporalPositionIdentifier")
                    else:
                        if 'GE' in self.scanner.manufacturer:
                            v = slc.get_tag_value((0x43,0x1039))[0]
                        else:
                            v = slc.get_tag_value((0x2001,0x1003))
                            try:
                                float(v)
                            except:
                                v = slc.get_tag_value((0x18,0x9087))
                    #if both way have tried but still None was returned
                    if v == None:
                        self.is_4D = False
                return v
            else:
                return None
                    
                
        if not skip_pixel_array:
            data = []
        keys = []
        for i,f in enumerate(self.files):
            slc = MRI_slice(f)
            if not skip_pixel_array:
                try:
                    slc_data = slc.get_pixel_array()
                except:
                    continue
                #data.append(slc.get_pixel_array())
                #Added an exception check to ensure non-DICOM file 
                #can be skipped.  ---Y.P. 11.18.2013
                data.append(slc_data)
            #tID = slc.get_tag_value(extra_dim_key)
            #zID = slc.get_tag_value(space_dim_key)
            tID = _get_extra_dim_key(slc)
            zID = _get_space_key(slc)
            instancen = slc.get_tag_value("InstanceNumber")
            keys.append((i, tID, zID, instancen))
            #print "f = %s ; t = %s ; z = %s"%(f, tID, zID)

        #remove variable
        del self.is_4D
        del self.DCE_seq
        #sort the keys by the second index first then the first index
        #  
        #  we need to sort the index-tID-zID tuples twice
        #  the first is to sort by location
        keys = sorted(keys, key=itemgetter(2))
        #  the second is to sort by time (or the extra dimension)
        keys = sorted(keys, key=itemgetter(1))

        #print keys

        #generate the cross mapping tables for instance, slice, and file numbers
        self._create_cross_ref_table_for_instance_slice_numbers(keys)
        
        #get RANKED file number, extra dimension indices, locations, and instance number
        ind, t, z, instancens = zip(*keys)

        #print ind
        #print t
        #print z
        
        #get the length of the two dimensions
        n_t = len(set(t))
        n_z = len(set(z))

        #print len(z)
        
        if n_t == 1:
            #double check if this is not 4D data
            if n_z != len(z):
                return self._get_pixel_array_4D(is_DCE_sequence=not is_DCE_sequence,
                                                skip_pixel_array=skip_pixel_array)

        if not skip_pixel_array:
            data = scipy.array(data)
            #print data.shape
            #print ind, t, z, instancens
            #print self.directory
        
            #have to convert tuple into list to make it work as an index
            data = data[list(ind)]

            #reshape the data
            #print n_t, n_z
            #print data.shape
            if n_t == 1:
                data.shape = [n_z] + list(data.shape[-2:])
            else:
                data.shape = [n_t, n_z] + list(data.shape[-2:])

        if n_t == 1:
            if not skip_pixel_array:
                self.data = data
                return_value = (False, data, keys)
            else:
                return_value = (False, keys)

        else:
            if not skip_pixel_array:
                self.data = data
                return_value = (True, data, keys)
            else:
                return_value = (True, keys)
        return return_value

    
    def _check_sequence_type(self):
        """
        Check a few keys to determine what sequence they are
        can tell difference between (T1, T2), DWI, DCE, DTI
        """
        """
        keys = ["DiffusionGradientOrientation", #DTI
                "Diffusionbvalue",              #DWI DTI
                "TriggerTime",                  #DCE
                "SliceLocation",                #all
                ]
        tag_dict = {}
        for k in keys:
            tag_dict[k] = []
        for f in self.files:
            dcm = dicom.ReadFile(f, stop_before_pixels=True,force=True)
            for key in keys:
                value = getattr(dcm,key, None)
                if value not in tag_dict[key]:
                    tag_dict[key].append(value)
        print tag_dict
        """
        identical_value, multiple_values = self._get_all_dicom_key_values()
        keys =  multiple_values.keys()
        if "TriggerTime" in keys:
            #this is DCE sequence for sure
            return 'DYN'
        else:
            #not sure
            return None
        
    def determine_sequence_type(self,check_all=False):
        """
        using scan description to determine the sequence type
        """
        if check_all:
            for f in self.files:
                dcm = MRI_slice(f)
                sd = dcm.get_scan_description()
                if sd != self.scan_description:
                    print "A scan description (other than %s) is found %s"%(self.scan_description,sd)
        seq_type = self.scan_description.suggest_sequence_type()
        #need to figure out the direction if it is a T2 sequence
        if seq_type == 'T2':
            ori = self.get_scan_direction()
            ori = "_"+ori[:3]
            seq_type += ori
        return seq_type
       
    def extract_voxel(self,p_coors, merge_to_one_slice=False):
        #calculate distance for the first slice
        """
        slice_keys = self.slices.keys()
        slice_keys.sort()
        slice0 = self.slices[slice_keys[0]]
        """
        filen = self.get_filen_from_slice_number(0)
        if type(filen) == type([]):
            filen = filen[0]
        if type(filen) == type(0.1):
            filen = int(filen)
        #print "@@@@@@@@@@@@@@@"
        #print "file number is %s"%filen
        #print "the selected file is %s"%self.files[filen]
        #print "@@@@@@@@@@@@@@@"
        slice0 = MRI_slice(self.files[filen])
        #print p_coors
        distance = slice0.distance_from_slice(p_coors)
        #print distance
        #ds = img0.get_slice_thickness()
        #ds = img0.get_spacing_between_slices()
        ds = slice0.get_tag_value("SpacingBetweenSlices")
        slicenumber = scipy.uint16(scipy.absolute(scipy.around(distance / ds)))
        coors = {}
        
        for i in range(slicenumber.size):
            slice_key = slicenumber[i]
            #sn = slicenumber[i]
            #if not coors.has_key(sn):
            if not coors.has_key(slice_key):
                coors[slice_key] = [p_coors[i]]
                #coors[sn] = [roi_patient_coors[i]]
            else:
                coors[slice_key].append(p_coors[i])
                
        if merge_to_one_slice and len(list(set(slicenumber))) != 1:
            print "Merge multiple slices"
            maxk = -1
            maxn = -1
            ncoors = []
            for key in coors.keys():
                if len(coors[key]) > maxn:
                    maxk = key
                    maxn = len(coors[key])
                ncoors.extend(coors[key])
            coors = {maxk: ncoors}

        #pprint.pprint(coors)
        #print coors.keys()
        for slice_key in coors.keys():
            try:
                sl = MRI_slice(self.files[slice_key])
            except:
                print "Could not find slice #%d in sequence %s"%(slice_key,self)
                print "using the last slice, instead."
                print "Please be caution using the returned coordinates."
                sl = MRI_slice(self.files[-1])
            coors[slice_key] = sl.convert_to_image_coors(coors[slice_key])
            
        return coors

    def __repr__(self):
        dirn = "/".join(self.directory.split("/")[-3:])
        return dirn + " (# slices: %d)"%len(self.files)
    def get_dicom_files(self):
        """
        get all dicom files in the sequence
        """
        #when no dicom files were specified
        #check the directory for the dicom files

        #files = os.listdir(self.directory)
        #files.sort()
        if self.files == None:
            self.files = []
            files = os.listdir(self.directory)
            files.sort()
            #print files
            for f in files:
                if os.path.isdir(os.path.join(self.directory,f)):pass
                else:
                    try:
                        dicom.read_file(os.path.join(self.directory,f))
                        self.files.append(os.path.join(self.directory,f))
                    except dicom.filereader.InvalidDicomError:
                        continue

    def get_pID(self):
        """
        figure out patient ID
        """
        pid = self.directory.split("/")[-3].split("_")[-1]
        try:
            ID = int(pid)
        except:
            #changed on 11/21/2013
            #to make sure this function returns an integer
            #ID = None
            ID = 99999
        return ID
    def get_modality(self):
        """
        Three values: MR, SC, and Pgs(???)
        """
        slc = MRI_slice(self.files[0])
        self.modality = slc.get_modality()
    def get_patient(self):
        """
        extract patient information
        """
        slc = MRI_slice(self.files[0])
        self.patient = slc.get_patient()
    def get_scanner(self):
        """
        extract scanner information
        """
        slc = MRI_slice(self.files[0])
        self.scanner = slc.get_scanner()
    def get_scan_date_time(self):
        """
        get information about when the scan was acquired
        """
        slc = MRI_slice(self.files[0])
        self.scan_time = slc.get_scan_date_time()
    def get_scan_description(self):
        """
        collect information about scan descript, protocol name, and others
        """
        slc = MRI_slice(self.files[0])
        self.scan_description = slc.get_scan_description()
    def get_series_number(self):
        self.series_number = MRI_slice(self.files[0]).get_tag_value("SeriesNumber")
        return self.series_number
    def get_scan_direction(self):
        ori = MRI_slice(self.files[0]).determine_orientation()
        return ori



if __name__=="__main__":
    #to debug the data reading function
    seqdir = "D:\\pydicom viewer\\pydicom\\anonymized_data_08272014\\000000\\401"
    seq = MRI_sequence(seqdir)

    seq.read_data()
    print seq.data.shape
