from imaplib import IMAP4
import smtplib
import time
from email.parser import HeaderParser

class SensorCorreo:
    def __init__(self, agente):
        self.agente = agente

    ###     Obtener tiempo de respuesta de IMAP EN MILISEGUNDOS
    def getTiempoRespIMAP(self):
        with IMAP4(self.agente.ip) as M:
            start = time.time()
            M.noop()
            return (time.time() - start) * 1000
        return 0

    def getTiempoRespSMTP(self):
        sender = 'carlos@localhost.com'
        receivers = ['carlos@localhost.com']
        message = 'Correo de prueba'
        try:
            smtpObj = smtplib.SMTP('localhost.com')
            start = time.time()
            smtpObj.sendmail(sender, receivers, message)
            print("Successfully sent email")
            return (time.time() - start) *1000
        except:
            print("Error: unable to send email")
            return 0

    def getTiempoResp(self):
        return self.getTiempoRespIMAP() + self.getTiempoRespSMTP()

    def getStatus(self):
        if self.getTiempoRespIMAP() == 0:
            return 'Down'
        if self.getTiempoRespSMTP() == 0:
            return 'Down'
        else:
            return 'Up'


"""
from Agente import Agente
from SensorCorreo import SensorCorreo

ag = Agente('127.0.0.1', 'v1', 'CarlosLopez4cv5', 'enp2s0')
s = SensorCorreo(ag)






"""
