import dicom
import numpy as scipy
from numpy import linalg
from MRI_sub_structures import MR_scan_description,scan_date_time
from MRI_sub_structures import patient, patients
from MRI_sub_structures import MR_scanner, MR_scanners

class MRI_slice:
    def __init__(self, filename):
        self.filename = filename
        self.dicom_open = False
    def __repr__(self):
        return '/'.join(self.filename.split('/')[-4:])
    def get_tag_value(self,tag):
        if not self.dicom_open:
            self.dcm = dicom.read_file(self.filename,stop_before_pixels=True,force=True)
            self.dicom_open = True
        #get value for a given tag
        dcm_value = self.dcm.get(tag, None)
        #if the tag was given as tag numbers,
        #the return value is a dicom.dataelem.DataElement instance
        #print dcm_value
        if type(dcm_value) is dicom.dataelem.DataElement:
            #print dcm_value
            value = dcm_value.value
        else:
            value = dcm_value
        return value
    def get_pixel_array(self):
        dcm = dicom.read_file(self.filename,stop_before_pixels=False,force=True)
        return dcm.pixel_array
    def determine_orientation(self):
        #this is working for the Philips scanner only
        #return self.get_tagvalue((0x2001,0x100b))
        ori = self.get_tag_value((0x2001,0x100b))
        #need to figure out other ways for the GE scanners
        #below works for GE scanners 12/21/10
        if ori == None:
            axesvectors = self.get_axes_orientation()
            maxv = scipy.absolute(axesvectors).max(0)
            ind = scipy.argmin(maxv)
            if ind == 0:
                ori = 'SAGITTAL'
            elif ind == 1:
                ori = 'CORONAL'
            elif ind == 2:
                ori = 'TRANSVERSE'
            else:
                ori = None
        return ori
    def get_axes_orientation(self):
        axesvectors = scipy.array(self.get_tag_value('ImageOrientationPatient'))
        #print axesvectors,self
        axesvectors.shape = (2,3)
        return axesvectors
    def get_norm_direction(self):
        axesvectors = self.get_axes_orientation()
        image_orientation = self.determine_orientation()
        if image_orientation == 'SAGITTAL':
            return scipy.cross(axesvectors[1,:], axesvectors[0,:])
        return scipy.cross(axesvectors[0,:], axesvectors[1,:])
    def convert_to_patient_coors(self,imagex, imagey,zoom_factor=1):
        axesvectors = self.get_axes_orientation()
        image_coors = scipy.array([imagex, imagey])
        image_coors.shape = (2,image_coors.size/2)
        #print "shapes: ",image_coors.shape, axesvectors.shape
        
        #convert to physical image coordinates
        real_coors = scipy.dot(image_coors.T,
                               scipy.diag(scipy.array(self.get_tag_value("PixelSpacing"))/zoom_factor))
        #convert into patient coordinates assuming left upper corner is (0,0,0)
        offset = scipy.dot(real_coors,axesvectors)
        #consider the coordinates of the left upper corner
        patient_coors = offset+scipy.array(self.get_tag_value('ImagePositionPatient'))
        return patient_coors
    def convert_to_image_coors(self, patient_coors):
        position = scipy.array(self.get_tag_value('ImagePositionPatient'))
        p_spacing = self.get_tag_value("PixelSpacing")
        
        offsets = scipy.array(patient_coors) - position
        zoom = linalg.inv(scipy.diag(p_spacing))
        image_coors = scipy.dot(offsets,self.get_axes_orientation().T)
        image_coors = scipy.around(scipy.dot(image_coors,zoom))
        image_coors = image_coors.tolist()
        unique_coors = []
        for coors in image_coors:
            if coors not in unique_coors:
                unique_coors.append(coors)
        return scipy.uint16(unique_coors)
    def distance_from_slice(self, patient_coors):
        position = scipy.array(self.get_tag_value('ImagePositionPatient'))
        return scipy.dot(patient_coors - position,
                         self.get_norm_direction().T)
    def get_patient(self):
        """
        extract patient information
        """
        pname = self.get_tag_value("PatientsName")
        patientid = self.get_tag_value("PatientID")
        bday = self.get_tag_value("PatientsBirthDate")
        weight = self.get_tag_value("PatientsWeight")
        p = patient(patientid, pname, bday, weight)
        return p
    def get_scanner(self):
        """
        extract scanner information
        """
        manuf = self.get_tag_value("Manufacturer")
        sname = self.get_tag_value("StationName")
        mname = self.get_tag_value("ManufacturersModelName")
        fstrg = self.get_tag_value("MagneticFieldStrength")
        sn = self.get_tag_value("DeviceSerialNumber")
        scanner = MR_scanner(manuf,fstrg,sname, mname, sn)
        return scanner
    def get_scan_date_time(self):
        """
        get information about when the scan was acquired
        """
        study_date = self.get_tag_value("StudyDate")
        study_time = self.get_tag_value("StudyTime")
        series_date = self.get_tag_value("SeriesDate")
        series_time = self.get_tag_value("SeriesTime")
        acquisition_date = self.get_tag_value("AcquisitionDate")
        acquisition_time = self.get_tag_value("AcquisitionTime")
        content_date = self.get_tag_value("ContentDate")
        content_time = self.get_tag_value("ContentTime")
        scan_time = scan_date_time(study_date, study_time,
                                   series_date, series_time,
                                   acquisition_date, acquisition_time,
                                   content_date, content_time)
        return scan_time
    def get_scan_description(self):
        series_description = self.get_tag_value("SeriesDescription")
        sequence_name = self.get_tag_value("SequenceName")
        protocol_name = self.get_tag_value("ProtocolName")
        scanning_sequence = self.get_tag_value("ScanningSequence")
        sequence_variant = self.get_tag_value("SequenceVariant")
        scan_options = self.get_tag_value("ScanOptions")
        scan_description = MR_scan_description(series_description,
                                               sequence_name,
                                               protocol_name,
                                               scanning_sequence,
                                               sequence_variant,
                                               scan_options)
        return scan_description
        
    def get_modality(self):
        return self.get_tag_value("Modality")
        

    def dicom_tree(self):
        from dicomtree import RunTree
        import Tix
        
        root = Tix.Tk()
        root.geometry("%dx%d%+d%+d" % (800, 600, 0, 0))
    
        RunTree(root, self.filename)
        root.mainloop()


if __name__ == "__main__":
    import os
    DOD_path = "D:\\pydicom viewer\\pydicom\\anonymized_data_08272014\\000000\\401"
    
    slc = MRI_slice(os.path.join(DOD_path, "IM_0400"))
    slc.dicom_tree()
