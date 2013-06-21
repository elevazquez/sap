import os
cur_dir = os.path.dirname(os.path.abspath(__file__))

from des.mod.Item import Item

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import navy, yellow, red

from geraldo import Report, ReportBand, landscape, Label, ObjectValue, SystemField, FIELD_ACTION_COUNT, FIELD_ACTION_SUM, BAND_WIDTH, Line, ReportGroup

class HistorialReporte(Report):
    title = 'Historial de Item'
    page_size = landscape(A4)
    margin_left = 2*cm
    
    class band_summary(ReportBand):
        height = 0.8*cm
        elements = [
            Label(text="Cantidad de Versiones de Item:", top=0.1*cm, left=0),
            ObjectValue(attribute_name='id', top=0.1*cm, left=5*cm,\
                action=FIELD_ACTION_COUNT, display_format='%s '),
        ]
        borders = {'all': True}

    class band_page_header(ReportBand):
        height = 1.3*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 16, 'alignment': TA_CENTER}),
            Label(text="Fase", top=0.8*cm, left=0*cm),
            Label(text="Tipo Item", top=0.8*cm, left=5*cm),
            Label(text="Codigo", top=0.8*cm, left=10*cm),
            Label(text="Version", top=0.8*cm, left=12*cm),
            Label(text="Descripcion", top=0.8*cm, left=15*cm),
            Label(text="Estado", top=0.8*cm, left=19*cm),
            Label(text="Costo", top=0.8*cm, left=21*cm),
            Label(text="Complejidad", top=0.8*cm, left=23*cm)
        ]
        borders = {'bottom': Line(stroke_color=red, stroke_width=3)}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='SAP - Sistema de Administracion de Proyectos', top=0.1*cm),
        ]
        borders = {'top': Line(stroke_color=navy)}

    class band_detail(ReportBand):
        height = 0.9*cm
        elements = [
            ObjectValue(attribute_name='id_fase', top=0, left=0*cm),
            ObjectValue(attribute_name='id_tipo_item', top=0, left=5*cm),
            ObjectValue(attribute_name='codigo', top=0, left=10*cm),
            ObjectValue(attribute_name='version', top=0, left=12*cm),
            ObjectValue(attribute_name='descripcion', top=0, left=15*cm),
            ObjectValue(attribute_name='estado', top=0, left=19*cm),
            ObjectValue(attribute_name='costo', top=0, left=21*cm),
            ObjectValue(attribute_name='complejidad', top=0, left=23*cm)
        ]