from ftplib import FTP
import time

class SensorFTP:
    def __init__(self, agente):
        self.agente = agente
        try:
            self.ftp = FTP(agente.ip)
        except ConnectionRefusedError:
            print("Servidor FTP: Down")
        return
    #Obtener tiempo de respuest EN MILISEGUNDOS
    def getTiempoResp(self):
        #ftp.login(user, pwd)
        start = time.time()
        self.ftp.getwelcome()
        respTime = time.time() - start
        return respTime * 1000

    def getStatus(self, user, pwd):
        try:
            self.ftp.login(user, pwd)
            return 'Up'
        except Exception:
             return 'Down'

    def getResp(self):
        return self.ftp.getwelcome()

    def getListaArchivos(self):
        ls = []
        self.ftp.dir(ls.append)
        return ls
