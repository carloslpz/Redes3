import rrdtool
import time
from SNMP import SNMP

class RRD:
    @staticmethod
    def crearRRD(host, dato):
        #DS:variable_name:DST:heartbeat:min:max
        start = str(time.time()).split('.')[0]
        return rrdtool.create( host + "/"+dato+".rrd",
            "--start",start,
            "--step",'60',
            "DS:"+dato+":GAUGE:600:U:U",
            "RRA:AVERAGE:0.5:6:576",
            "RRA:AVERAGE:0.5:1:144")

    @staticmethod
    def updateAgente(agente, datos):
        while True:
            for dato in datos:
                valor = int(SNMP.consulta(agente, dato[1]))
                valor = "N:"+ str(valor)
                #print("Introduciendo {}.{}: {}".format(agente.ip, dato[0], valor))
                rrdtool.update( agente.ip+ '/'+ dato[0]+ '.rrd', valor)
        return

    @staticmethod
    def generarGrafica(agente, ventana, dato):
        tiempoActual = int(time.time())
        tiempoFinal = tiempoActual - 60
        tiempoInicial = tiempoFinal - (60 * int(ventana))
        print("Generando gráfica de {}: {}".format(agente.ip, dato))
        rrdtool.graph( agente.ip + "/"+dato+ ".png",
                        "--start",str(tiempoInicial),
    #                    "--end","N",
                        "--vertical-label="+'Bytes/s'+"",
                        "DEF:"+dato+"="+agente.ip+"/"+dato+".rrd:"+dato+":AVERAGE",
                        "DEF:"+dato+"="+agente.ip+"/"+dato+".rrd:"+dato+":AVERAGE",
                        "AREA:"+dato+"#00FF00:"+dato+"\r")
        return
