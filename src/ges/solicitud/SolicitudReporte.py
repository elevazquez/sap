import os
cur_dir = os.path.dirname(os.path.abspath(__file__))
from ges.mod.SolicitudCambio import SolicitudCambio
from ges.mod.SolicitudItem import SolicitudItem

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import navy, yellow, red

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField, FIELD_ACTION_COUNT, FIELD_ACTION_SUM, BAND_WIDTH, Line, ReportGroup, SubReport

class SolicitudReporte(Report):
    title = 'Solicitudes de Cambio'

    class band_summary(ReportBand):
        height = 0.8*cm
        elements = [
            Label(text="Cantidad de Solicitudes:", top=0.1*cm, left=0),
            ObjectValue(attribute_name='id', top=0.1*cm, left=4*cm,\
                action=FIELD_ACTION_COUNT, display_format='%s '),
        ]
        borders = {'all': True}

    class band_page_header(ReportBand):
        height = 1.3*cm
        elements = [
            SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}),
            Label(text="Fecha", top=0.8*cm, left=5*cm),
            Label(text="Usuario", top=0.8*cm, left=9*cm),
            Label(text="Estado", top=0.8*cm, left=12*cm),
            Label(text="Voto", top=0.8*cm, left=15*cm)
        ]
        borders = {'bottom': Line(stroke_color=navy)}

    class band_page_footer(ReportBand):
        height = 0.5*cm
        elements = [
            Label(text='SAP - Sistema de Administracion de Proyectos', top=0.1*cm),
        ]
        borders = {'top': Line(stroke_color=navy)}

    class band_detail(ReportBand):
        height = 0.7*cm
        elements = [
            ObjectValue(attribute_name='fecha', top=0, left=5*cm),
            ObjectValue(attribute_name='id_usuario', top=0, left=9*cm),
            ObjectValue(attribute_name='estado', top=0, left=12*cm),
            ObjectValue(attribute_name='cant_votos', top=0, left=15*cm, 
                        get_value=lambda instance: instance.cant_votos!=None and 'Si' or 'No')
        ]

    groups = [
        ReportGroup(attribute_name='id',
            band_header=ReportBand(
                height=1*cm,
                elements=[
                    ObjectValue(attribute_name='id', left=0, top=0.1*cm,
                        get_value=lambda instance: 'Solicitud: ' + (instance.descripcion),
                        style={'fontName': 'Helvetica-Bold', 'fontSize': 12})
                ],
                borders={'bottom': True},
            ),
#            band_footer=ReportBand(
#                height=0.7*cm,
#                elements=[
#                    Label(text="Items en la Solicitud:", top=0.1*cm, left=0),
#                    ObjectValue(attribute_name='id', action=FIELD_ACTION_COUNT,
#                        display_format='%s ', left=4*cm, top=0.1*cm),
#                ],
#                borders={'all': True},
#            ),
        ),
    ]
    
    subreports = [
         SubReport(
             queryset_string = '%(object)s. detalle(%(object)s.id)',
#             queryset_string = '%(object)s. db_session.query(LineaBase).from_statement(select lb.* from solicitud_item si, linea_base lb, lb_item lbi where si.id_solicitud=20 ' 
#             ' and si.id_item = lbi.id_item and lbi.id_linea_base = lb.id order by lb.descripcion ).all()',
             band_header = ReportBand(
                     height=0.5*cm,
                     elements=[
                         Label(text='Linea Base', top=0, left=0.2*cm, style={'fontName': 'Helvetica-Bold'}),
                         Label(text='Id', top=0, left=4*cm, style={'fontName': 'Helvetica-Bold'}),
                         Label(text='Descripcion', top=0, left=8*cm, style={'fontName': 'Helvetica-Bold'}),
                     ],
                     borders={'top': True, 'left': True, 'right': True},
                 ),
             band_detail = ReportBand(
                     height=0.5*cm,
                     elements=[
                         ObjectValue(attribute_name='id', top=0, left=4*cm),
                         ObjectValue(attribute_name='descripcion', top=0, left=8*cm),
                     ],
                     borders={'left': True, 'right': True},
                 ),
             band_footer = ReportBand(
                     height=0.5*cm,
                     elements=[
                         ObjectValue(attribute_name='id', left=8*cm,\
                             action=FIELD_ACTION_COUNT, display_format='%s lineas base en la Solicitud',
                             style={'fontName': 'Helvetica-Bold'}),
                     ],
                     borders={'bottom': True, 'left': True, 'right': True},
                 ),
         ),
     ]