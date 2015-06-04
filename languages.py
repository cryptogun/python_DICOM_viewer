# -*- coding: utf-8 -*-
'''
This is the languages package. You can add new language(s) as the form below.
'''

#Languages package table. Format: shorten meaning mark: meaning
table = \
{
'English' : {'title': 'Python DICOM Viewer', 'm_file': 'File', 'm_edit': 'Edit', 'm_view': 'View', 'm_image': 'Image', 'm_ROI': 'ROI', 'm_measure': 'Measure', 'm_help': 'Help', 'm_open_single': 'Open  DICOM File', 'm_open_series': 'Open Series', 'm_save_as': 'Save As', 'm_convert_as': 'Convert As','m_convert_all_as':'Convert All As', 'm_exit': 'Exit', 'm_undo': 'Undo', 'm_redo': 'Redo', 'm_tags': 'Tags Display: ', 'm_tag1': 'Tag1', 'm_zoom': 'Zoom', 'm_ori_size': 'Original Size', 'm_zoom_in': 'Zoom In', 'm_zoom_out': 'Zoom Out', 'm_fit_win': 'Fit Window', 'm_fit_wid': 'Fit Width', 'm_fit_hei': 'Fit Height', 'm_slide_show': 'Slide Show', 'm_ro_180': 'Turn 180°', 'm_ro_90': 'Turn left', 'm_ro_270': 'Turn Right', 'm_filp_hori': 'Flip Horizontal', 'm_filp_vert': 'Flip Vertical', 'm_ro_flip_default': 'Back to Default', 'm_draw_edit': 'Edit', 'm_save_ROIs': 'Save ROI(s)', 'm_load_ROIs': 'Load ROI(s)', 'm_distance': 'Distance', 'm_size': 'Size', 'm_stat_in_ROI': 'Statistics in ROI', 'm_about': 'About This Program...', 'm_contact_author': 'Contact Author', 'tags detail': 'Tags Detail', 'invalidDCMerr_msg': 'It is not a valid DICOM file.', 'ROI_dra_discription': 'Draw Discription'},
'简体中文' : {'title': 'Python DICOM 图像浏览器', 'm_file': '文件', 'm_edit': '编辑', 'm_view': '查看', 'm_image': '图像', 'm_ROI': '兴趣区域', 'm_measure': '测量', 'm_help': '帮助', 'm_open_single': '打开DICOM文件', 'm_open_series': '打开系列', 'm_save_as': '另存为', 'm_convert_as': '转换格式为','m_convert_all_as':'批量转换为', 'm_exit': '退出', 'm_undo': '撤销', 'm_redo': '重做', 'm_tags': '标签选择：', 'm_tag1': 'Tag1', 'm_zoom': '缩放', 'm_ori_size': '原始尺寸', 'm_zoom_in': '放大', 'm_zoom_out': '缩小', 'm_fit_win': '适应屏幕', 'm_fit_wid': '适应宽度', 'm_fit_hei': '适应高度', 'm_slide_show': '幻灯片放映', 'm_ro_180': '旋转180°', 'm_ro_90': '左转90°', 'm_ro_270': '右转90°', 'm_filp_hori': '水平翻转', 'm_filp_vert': '垂直翻转', 'm_ro_flip_default': '返回初始状态', 'm_draw_edit': '编辑批注', 'm_save_ROIs': '保存ROI到……', 'm_load_ROIs': '加载ROI从……', 'm_distance': '长度', 'm_size': '尺寸', 'm_stat_in_ROI': 'ROI内的统计数据', 'm_about': '关于本程序...', 'm_contact_author': '联系作者', 'tags detail': '标签详细信息', 'invalidDCMerr_msg': '这不是有效的DICOM文件。', 'ROI_dra_discription': '标记与批注绘制说明'}
}

#Get all valid languages name from table above.
languages = tuple(i for i in table.keys())
