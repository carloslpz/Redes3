# header_footer.py
from fpdf import FPDF
from Agente import Agente
from SNMP import SNMP
from SensorCorreo import SensorCorreo
from SensorHTTP import SensorHTTP
from SensorDNS import SensorDNS
from SensorFTP import SensorFTP
from SensorSSH import SensorSSH

class PDF(FPDF):
    def header(self):
        # Set up a logo
        self.set_font('Arial', 'B', 15)
        # Add an address
        self.cell(50)
        self.cell(0, 5, 'Reporte de agente', ln=1)
        # Line break
        self.ln(20)

    def footer(self):
        self.set_y(-10)

        self.set_font('Arial', 'I', 8)

        # Add a page number
        page = 'Página ' + str(self.page_no()) + '/{nb}'
        self.cell(0, 10, page, 0, 0, 'C')


def create_pdf(pdf_path, agente):
    pdf = PDF()
    correo = SensorCorreo(agente)
    http = SensorHTTP(agente)
    dns = SensorDNS(agente)
    ftp = SensorFTP(agente)
    ssh = SensorSSH(agente)

    # Create the special value {nb}
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    #Información de introducción
    pdf.cell(75,5, 'Integrante Carlos Isaí López Reséndiz', 1)
    pdf.cell(35,5, 'Fecha: 29/06/20', 1)
    pdf.cell(0,5, 'Sistema Operativo: {}'.format(SNMP.consulta(agente, '1.3.6.1.2.1.1.1.0')), 1,1)
    pdf.cell(80,5, 'Tiempo de actividad del servidor: {}s'.format(int(SNMP.consulta(agente, '1.3.6.1.2.1.1.3.0'))/100), 1)
    pdf.cell(0,5, 'Número de interfaces: {}'.format(SNMP.consulta(agente, '1.3.6.1.2.1.2.1.0')), 1,1)
    #Gráficas
    pdf.cell(0,8, 'CPU', 1,1,'C')
    pdf.cell(0,80, '', 1,1)
    pdf.image(agente.ip+'/CPUPercUser.png', pdf.get_x()+10, pdf.get_y()-70, 0)
    pdf.cell(0,8, 'RAM', 1,1,'C')
    pdf.cell(0,80, '', 1,1)
    pdf.image(agente.ip+'/RAMUsd.png', pdf.get_x()+10, pdf.get_y()-70, 0)
    pdf.add_page()
    pdf.cell(0,8, 'Disco Duro', 1,1,'C')
    pdf.cell(0,80, '', 1,1)
    pdf.image(agente.ip+'/HDDUsdPerc.png', pdf.get_x()+10, pdf.get_y()-70, 0)
    pdf.add_page()
    #Sensores
    pdf.cell(0,8, 'Supervisión de servidores', 1,1,'C')
    pdf.cell(0,8, 'Sensor de correo', 1,1)
    if correo.getStatus() == 'Up':
        pdf.cell(0,5, 'Status: Up',0,1)
        pdf.cell(0,5, 'Tiempo de respuesta del servidor SMTP: {}'.format(correo.getTiempoRespSMTP()),0,1)
        pdf.cell(0,5, 'Tiempo de respuesta del servidor IMAP: {}'.format(correo.getTiempoRespIMAP()),0,1)
        pdf.cell(0,5, 'Tiempo de respuesta acumulado: {}'.format(correo.getTiempoResp()),0,1)
    else:
        pdf.cell(0,5, 'Status: Down',0,1)
    pdf.cell(0,5, '*Tiempos mostrados en milisegundos',0,1)

    pdf.cell(0,8, 'Sensor de Información', 1,1)
    if http.getStatus() == 'Up':
        pdf.cell(0,5, 'Status: Up',0,1)
        pdf.cell(0,5, 'Tiempo de respuesta de solicitud POST: {}'.format(http.getTiempoResp()),0,1)
        pdf.cell(0,5, 'Número de bytes recibidos: {}'.format(http.getNumBytesRecv()),0,1)
        pdf.cell(0,5, 'Ancho de banda de descarga: {}'.format(http.getDwBandw()),0,1)
    else:
        pdf.cell(0,5, 'Status: Down',0,1)
    pdf.cell(0,5, '*Tiempos mostrados en milisegundos',0,1)

    pdf.cell(0,8, 'Sensor de Archivos', 1,1)
    if ftp.getStatus('u1','123456') == 'Up':
        pdf.cell(0,5, 'Status: Up',0,1)
        pdf.cell(0,5, 'Tiempo de respuesta: {}'.format(ftp.getTiempoResp()),0,1)
        pdf.cell(0,5, 'Respuesta: {}'.format(ftp.getResp()),0,1)
        pdf.cell(0,5, 'Archivos',0,1)
        for arch in ftp.getListaArchivos():
            pdf.cell(0,5, str(arch),0,1)
    else:
        pdf.cell(0,5, 'Status: Down',0,1)

    pdf.cell(0,8, 'Sensor DNS', 1,1)
    if dns.getStatus('zona.carloslopez4cm3.com') == 'Up':
        pdf.cell(0,5, 'Status: Up',0,1)
        pdf.cell(0,5, 'Tiempo de respuesta: {}'.format(dns.getTiempoResp('zona.carloslopez4cm3.com')),0,1)
    else:
        pdf.cell(0,5, 'Status: Down',0,1)

    pdf.cell(0,8, 'Sensor de Acceso', 1,1)
    if ssh.getStatus('carlos','123456') == 'Up':
        pdf.cell(0,5, 'Status: Up',0,1)
        pdf.cell(0,5, 'Número de conexiones activas: {}'.format(ssh.getNumConexiones()),0,1)
        pdf.cell(0,5, 'Tiempo activo de las respuestas',0,1)
        for t in ssh.getTiempoAct():
            pdf.cell(0,5, str(t),0,1)
    else:
        pdf.cell(0,5, 'Status: Down',0,1)

    #Crear PDF
    pdf.output(pdf_path)


if __name__ == '__main__':
    ag = Agente('127.0.0.1', 'v1', 'CarlosLopez4cv5', 'enp2s0')
    create_pdf('reporte.pdf', ag)
