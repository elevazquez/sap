import os
cur_dir = os.path.dirname(os.path.abspath(__file__))

from ges.mod.SolicitudCambio import SolicitudCambio

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import navy, yellow, red

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField, FIELD_ACTION_COUNT, FIELD_ACTION_SUM, BAND_WIDTH, Line, ReportGroup

class SolicitudReporte(Report):
    title = 'Solicitudes de Cambio'

    class band_summary(ReportBand):
        height = 0.8*cm
        elements = [
            Label(text="Users count:", top=0.1*cm, left=0),
            ObjectValue(attribute_name='id', top=0.1*cm, left=4*cm,\
                action=FIELD_ACTION_COUNT, display_format='%s users found'),
        ]
        borders = {'all': True}

    class band_page_header(ReportBand):
        height = 1.3*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
            Label(text="ID usu", top=0.8*cm, left=0),
            Label(text="Descripcion", top=0.8*cm, left=3*cm),
            Label(text="Estado", top=0.8*cm, left=8*cm)
        ]
        borders = {'bottom': Line(stroke_color=red, stroke_width=3)}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='SAP Sistema de Administracion de Proyectos', top=0.1*cm),
        ]
        borders = {'top': Line(stroke_color=navy)}

    class band_detail(ReportBand):
        height = 0.7*cm
        elements = [
            ObjectValue(attribute_name='id_usuario', top=0, left=1*cm),
            ObjectValue(attribute_name='descripcion', top=0, left=3*cm),
            ObjectValue(attribute_name='estado', top=0, left=13*cm)
        ]

#    groups = [
#        ReportGroup(attribute_name='is_superuser',
#            band_header=ReportBand(
#                height=0.7*cm,
#                elements=[
#                    ObjectValue(attribute_name='is_superuser', left=0, top=0.1*cm,
#                        get_value=lambda instance: 'Superuser: ' + (instance.is_superuser and 'Yes' or 'No'),
#                        style={'fontName': 'Helvetica-Bold', 'fontSize': 12})
#                ],
#                borders={'bottom': True},
#            ),
#            band_footer=ReportBand(
#                height=0.7*cm,
#                elements=[
#                    ObjectValue(attribute_name='id', action=FIELD_ACTION_COUNT,
#                        display_format='%s superusers', left=0*cm, top=0.1*cm),
#                    ObjectValue(attribute_name='id', action=FIELD_ACTION_SUM,
#                        display_format='%s is the sum of IDs above', left=4*cm, top=0.1*cm),
#                ],
#                borders={'top': True},
#            ),
#        ),
#        ReportGroup(attribute_name='is_staff',
#            band_header=ReportBand(
#                height=0.7*cm,
#                elements=[
#                    ObjectValue(attribute_name='is_staff', left=0.5*cm, top=0.1*cm,
#                        get_value=lambda instance: 'Staff: ' + (instance.is_staff and 'Yes' or 'No'))
#                ],
#                borders={'bottom': True},
#            ),
#            band_footer=ReportBand(
#                height=0.7*cm,
#                elements=[
#                    ObjectValue(attribute_name='id', action=FIELD_ACTION_COUNT,
#                        display_format='%s staffs', left=0.5*cm, top=0.1*cm)
#                ],
#                borders={'top': True},
#            ),
#        ),
#    ]