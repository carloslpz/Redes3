import requests
import time

class SensorHTTP:
    def __init__(self, agente):
        self.agente = agente

    ##Obtener tiempo de respuesta EN MILISEGUNDOS
    def getTiempoResp(self):
        start = time.time()
        r = requests.post('http://{}'.format(self.agente.ip))
        return (time.time()-start)*1000
    ##Obtener número de Bytes recibidos
    def getNumBytesRecv(self):
        r = requests.get('http://{}'.format(self.agente.ip), stream=True)
        return len(r.raw.read())

    def getDwBandw(self):
        start = time.time()
        r = requests.get('http://{}'.format(self.agente.ip), stream=True)
        dwTime = time.time() - start
        kB = len(r.raw.read())/1000
        return (kB/dwTime)

    def getStatus(self):
        try:
            r = requests.get('http://{}'.format(self.agente.ip))
            return 'Up'
        except:
            return 'Down'
