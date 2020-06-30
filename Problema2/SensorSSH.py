import subprocess
from paramiko import client
import datetime

class SensorSSH:
    def __init__(self, agente):
        self.agente = agente

    def getConexiones(self):
        res = subprocess.run(['w'], stdout = subprocess.PIPE)
        conexiones = res.stdout.decode('utf-8').split('\n')
        for i,con in enumerate(conexiones):
            if '?xdm?' in con:
                conexiones.pop(i)
        return conexiones

    def getNumConexiones(self):
        conx = self.getConexiones()
        return len(conx) - 2 #Se resta por un renglón vacío y el de cabeceras

    def getTiempoAct(self):
        tiempos = []
        conx = self.getConexiones()
        for i,c in enumerate(conx):
            try:
                hora = str(c).split()[3]
                hora = datetime.datetime.strptime(hora, '%H:%M').time()
                hFechaI = datetime.datetime.combine(datetime.date.today(), hora)
                tiempos.append(datetime.datetime.now() - hFechaI)
            except:
                pass
        return tiempos

    def getStatus(self, user, pwd):
        cl = client.SSHClient()
        cl.load_system_host_keys()
        try:
            cl.connect(self.agente.ip, 22, 'carlos', '123456')
            return 'Up'
        except:
            return 'Down'

from Agente import Agente
from SensorSSH import SensorSSH
ag = Agente('127.0.0.1', 'v1', 'CarlosLopez4cv5', 'enp2s0')
s = SensorSSH(ag)
