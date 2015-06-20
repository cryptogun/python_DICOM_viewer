from distutils.core import setup
import py2exe

Mydata_files = [('images', ['D:\\pydicom viewer/python DICOM viewer/images/flip_hori.gif']),
('images', ['D:\\pydicom viewer/python DICOM viewer/images/flip_vert.gif']),
('images', ['D:\\pydicom viewer/python DICOM viewer/images/icon.ico']),
('images', ['D:\\pydicom viewer/python DICOM viewer/images/icon.xbm']),
('images', ['D:\\pydicom viewer/python DICOM viewer/images/turn_180.gif']),
('images', ['D:\\pydicom viewer/python DICOM viewer/images/turn_left.gif']),
('images', ['D:\\pydicom viewer/python DICOM viewer/images/turn_right.gif']),
]#(['settings.ini'])

setup(
    console=['GUI.py'],
    data_files = Mydata_files,
    windows=["GUI.py"]
)