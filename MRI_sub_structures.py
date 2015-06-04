class MR_scan_description:
    def __init__(self,series_description, sequence_name,protocol_name,
                scanning_sequence,sequence_variant, scan_options,):
        self.series_description = series_description
        self.sequence_name = sequence_name
        self.protocol_name = protocol_name
        self.scanning_sequence = scanning_sequence
        self.sequence_variant = sequence_variant
        self.scan_options = scan_options
    def suggest_sequence_type(self):
        #add T2W_MAP 7/24/13
        key_words = ['T2W_MAP', 'T1', 'T2', 'DW', 'ADC','APPARENT DIFFUSION COEFFICIENT',
                     'PRE', 'POST','DELAY','DYN', 'DCE','MRS','TENSOR',
                     'CITRATE','3 PLN LOC','SURVEY','CAL','SCREENSAVE',
                     'PERFUSION COLORMAPS']
        pulse = None
        sd = self.series_description
        pn = self.protocol_name
        for tag in (sd, pn):
            for key in key_words:
                if tag != None and key in tag.upper():
                    pulse = key
                    break
            if pulse != None:
                break
        if pulse == 'APPARENT DIFFUSION COEFFICIENT':
            pulse = 'ADC'
        elif pulse == 'DCE':
            pulse = 'DYN'
        elif pulse == 'DELAY':
            pulse = 'POST'
        elif pulse == '3 PLN LOC':
            pulse = 'SURVEY'
        elif pulse == 'CITRATE':
            pulse = 'MRS'
        elif pulse == None:
            #print "Cannot identify this sequence: %s: SD = %s; PN = %s"%(self, sd, pn)
            pass
        return pulse
        
    def __str__(self):
        return "%s; %s; %s"%(self.series_description,
                             self.sequence_name,
                             self.protocol_name)
    def __eq__(self,other):
        if self.series_description == other.series_description and \
               self.sequence_name == other.sequence_name and \
               self.protocol_name == other.protocol_name and \
               self.scanning_sequence == other.scanning_sequence and \
               self.sequence_variant == other.sequence_variant and \
               self.scan_options == other.scan_options:
            return True
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
        

class scan_date_time:
    def __init__(self,study_date, study_time,
                 series_date, series_time,
                 acquisition_date, acquisition_time,
                 content_date, content_time):
        self.study_date = study_date
        self.study_time = study_time
        self.series_date = series_date
        self.series_time = series_time
        self.acquisition_date = acquisition_date
        self.acquisition_time = acquisition_time
        self.content_date = content_date
        self.content_time = content_time
    def __repr__(self):
        if self.study_date == self.series_date == \
               self.acquisition_date == self.content_date:
            return "Scan performed on %s"%self.study_date
        else:
            return "Scan dates: %s, %s, %s, %s"%(self.study_date,
                                                 self.series_date,
                                                 self.acquisition_date,
                                                 self.content_date)
    def __eq__(self, other):
        if self.study_date == other.study_date and \
           self.study_time == study_time and \
           self.series_date == series_date and \
           self.series_time == series_time and \
           self.acquisition_date == acquisition_date and \
           self.acquisition_time == acquisition_time and \
           self.content_date == content_date and \
           self.content_time == content_time:
            return True
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)

class patient:
    def __init__(self, patientID, name, birth_day, weight):
        self.name = name
        self.ID = patientID
        self.birth_day = birth_day
        self.weight = weight
    def __repr__(self):
        return "Patient %s (b-date %s, %d kg)"%(self.name,
                                                self.birth_day,
                                                self.weight)
    def __eq__(self, other):
        if self.name == other.name and \
           self.birth_day == other.birth_day and \
           self.ID == other.ID and \
           self.weight == other.weight:
            return True
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)

class patients:
    def __init__(self):
        self.patient_list = {}
    def add_patient(self, pID, patient):
        self.patient_list[pID] = patient
    def get_patient(self, pID):
        return self.patient_list.get(pID, None)

class MR_scanner:
    def __init__(self, manufacturer, field_strength,
                 scanner_name, model_name,sn):
        self.manufacturer = manufacturer
        self.field_strength = field_strength
        self.station_name = scanner_name
        self.model_name = model_name
        self.device_serial_number = sn
    def __repr__(self):
        return "%s (%3.1f %s S/N: %s Name: %s)"%(self.model_name,
                                                self.field_strength,
                                                self.manufacturer,
                                                self.device_serial_number,
                                                self.station_name,)
    def __eq__(self, other):
        if self.manufacturer == other.manufacturer and \
           self.field_strength == other.field_strength and \
           self.station_name == other.station_name and \
           self.device_serial_number == other.device_serial_number:
            return True
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
class MR_scanners:
    def __init__(self):
        self.scanner_list = []
    def add_scanner(self, scanner):
        self.scanner_list.append(scanner)
    def has_scanner(self, scanner):
        if scanner in self.scanner_list:
            return self.scanner_list.index(scanner)
        else:
            return None
    def get_scanner(self, index):
        return self.scanner_list[index]
def test_scanners_class():
    scanner1 = MR_scanner("GE", 1.5, "dkfje")
    scanner2 = MR_scanner("GE", 1.5, "dkfje")
    scanner3 = MR_scanner("GE", 1.5, "dkfk")
    scanners = MR_scanners()
    scanners.add_scanner(scanner1)
    scanners.add_scanner(scanner3)
    ind = scanners.has_scanner(scanner2)
    if ind != None:
        print "there is a scanner %s in the list"%scanner2
    print scanners.get_scanner(ind)
    print scanners.get_scanner(1)

