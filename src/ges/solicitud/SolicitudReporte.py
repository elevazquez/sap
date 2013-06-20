import os
cur_dir = os.path.dirname(os.path.abspath(__file__))

from ges.mod.SolicitudCambio import SolicitudCambio

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField,FIELD_ACTION_COUNT, BAND_WIDTH


class SolicitudReporte(Report):
    title = 'Lista de Solicitudes de Cambio'

    class band_begin(ReportBand):
        height = 1*cm
        elements = [
            Label(text='Mira estas solicitudes', top=0.1*cm,
                left=8*cm),
        ]

    class band_summary(ReportBand):
        height = 0.7*cm
        elements = [
            Label(text="Eso es todo", top=0.1*cm, left=0),
            ObjectValue(attribute_name='descripcion', top=0.1*cm, left=3*cm,
                action=FIELD_ACTION_COUNT,
                display_format='%s solicitudes encontradas'),
        ]
        borders = {'all': True}

    class band_page_header(ReportBand):
        height = 1.3*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm,
                left=0, width=BAND_WIDTH, style={'fontName': 'Helvetica-Bold',
                'fontSize': 14, 'alignment': TA_CENTER}),
            Label(text="ID", top=0.8*cm, left=0),
            Label(text="Descripcion", top=0.8*cm, left=3*cm),
        ]
        borders = {'bottom': True}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='Pie de pagina', top=0.1*cm, left=0),
            SystemField(expression='Page # %(page_number)d of %(page_count)d', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
        ]
        borders = {'top': True}

    class band_detail(ReportBand):
        height = 0.5*cm
        elements = [
            ObjectValue(attribute_name='id', top=0, left=0),
            ObjectValue(attribute_name='descripcion', top=0, left=3*cm, width=7*cm),
        ]