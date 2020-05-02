from os import system
from pysnmp.hlapi import *
import os
import rrdtool
import time
import threading
from subprocess import Popen, PIPE
from fpdf import FPDF

def agregarUsuario(ip, vSNMP, comm, adapt):
    #time.tzset()
    f = open("agentes.txt", "a+")
    system("mkdir " + ip)
    f.write(ip + ' '+ vSNMP+ ' '+ comm+ ' '+ adapt + '\n')
    crearTodoRRD(ip)
    f.close()
    return True

def eliminarUsuario(ip):
    print("Eliminando usuario " + ip)
    with open("agentes.txt", "r") as f:
        lines = f.readlines()
    with open("agentes.txt", "w") as f:
        for line in lines:
            if line.split()[0] != ip:
                f.write(line)
    system("rmdir " + ip)
    return True

def consultaSNMP(comunidad,host,oid):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(comunidad),
                   UdpTransportTarget((host, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid))))

        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                varB=(' = '.join([x.prettyPrint() for x in varBind]))
                resultado= varB.split()[2]
        return resultado

def imprimirEstado():
    agentes = []
    comunidades = []
    with open("agentes.txt", "r") as f:
        lineas = f.readlines()
    for line in lineas:
        agentes.append(line.split()[0])
        comunidades.append(line.split()[2])
    print("Número de agentes: " + str(len(agentes)))
    for i in range(len(agentes)):
        print("\t\t\t" + agentes[i])
        print("Estado del agente: ")
        if ping(agentes[i]) == 0:
            print("up")
        else:
            print("down")
        print("Número de interfaces:")
        print(consultaSNMP(comunidades[i], agentes[i], '1.3.6.1.2.1.2.1.0'))
        #print(" " + consultaSNMP())

def ping(ip):
    return os.system("ping -c 1 " + ip)

def crearRRD(host, dato):
     #DS:variable_name:DST:heartbeat:min:max
     start = str(time.time()).split('.')[0]
     return rrdtool.create( host + "/"+dato+".rrd",
                         "--start",start,
                         "--step",'60',
                         "DS:"+dato+":COUNTER:600:U:U",
                         "RRA:AVERAGE:0.5:6:576",
                         "RRA:AVERAGE:0.5:1:144")

def crearTodoRRD(host):
    crearRRD(host, 'inMCast')
    crearRRD(host, 'inPkt')
    crearRRD(host, 'rspICMP')
    crearRRD(host, 'outSeg')
    crearRRD(host, 'inErrDGram')

def updateHost(host, comunidad):
    while True:
        #1)
        inMCast = 0 #int(
            #consultaSNMP('grupo4cv5', host,
            #             '1.3.6.1.2.1.31.1.1.1.2.0'))"""
        valor = "N:"+ str(inMCast)#+ ':'+ str(inMCast)
        #print(host+ ': '+valor)
        rrdtool.update( host+ '/inMCast.rrd', valor)
        #2)
        inPkt = int(
            consultaSNMP(comunidad, host,
                         '1.3.6.1.2.1.4.9.0'))
        valor = "N:"+ str(inPkt)#+ ':'+ str(inPkt)
        #print(host+ ': '+valor)
        rrdtool.update( host+ '/inPkt.rrd', valor)
        #3)
        rspICMP = int(
             consultaSNMP(comunidad, host,
                          '1.3.6.1.2.1.5.21.0'))
        valor = "N:"+ str(rspICMP)#+ ':'+ str(rspICMP)
        #print(host+ ': '+valor)
        rrdtool.update( host+ '/rspICMP.rrd', valor)
        #4)
        outSeg = int(
            consultaSNMP(comunidad, host,
                         '1.3.6.1.2.1.6.11.0'))
        valor = "N:"+ str(outSeg)#+ ':'+ str(outSeg)
        #print(host+ ': '+valor)
        rrdtool.update( host+ '/outSeg.rrd', valor)
        #5)
        inErrDGram = int(
            consultaSNMP(comunidad, host,
                         '1.3.6.1.2.1.7.3.0'))
        valor = "N:"+ str(inErrDGram)#+ ':'+ str(inErrDGram)
        #print(host+ ': '+valor)
        rrdtool.update( host+ '/inErrDGram.rrd', valor)

def updateTodo():
    threads = []
    agentes = []
    comunidades = []
    with open("agentes.txt", "r") as f:
        lineas = f.readlines()
    for line in lineas:
        agentes.append(line.split()[0])
        comunidades.append(line.split()[2])
    print("Número de agentes: " + str(len(agentes)))
    for i in range(len(agentes)):
        t = threading.Thread(target=updateHost,args=(agentes[i], comunidades[i]))
        threads.append(t)
        t.start()

def updateTraficoInterfaz(ip, numInterfaz):
    while True:
        trafIn = int(consultaSNMP('CarlosLopez4cv5', ip,  '1.3.6.1.2.1.2.2.1.10.' + str(numInterfaz)))
        valor = "N:"+ str(trafIn)
        rrdtool.update( ip+ '/in.rrd', valor)

        trafOut = int(consultaSNMP('CarlosLopez4cv5', ip,  '1.3.6.1.2.1.2.2.1.16.' + str(numInterfaz)))
        valor = "N:"+ str(trafOut)
        rrdtool.update( ip+ '/out.rrd', valor)
def correrHiloTraficoInterfaz(ip,  numInterfaz):
    threads = []
    t = threading.Thread(target=updateTraficoInterfaz, args=(ip, numInterfaz))
    t.start()


def updateTraficoProtocolo(ip, ind):
    while True:
        if ind == '0':  #TCP
            inOID = '1.3.6.1.2.1.6.10.0'
            outOID ='	1.3.6.1.2.1.6.11.0'
        else:
            inOID = '1.3.6.1.2.1.7.1.0'
            outOID ='1.3.6.1.2.1.7.4.0'
        trafIn = int(consultaSNMP('CarlosLopez4cv5', ip,  inOID))
        valor = "N:"+ str(trafIn)
        rrdtool.update( ip+ '/in.rrd', valor)

        trafOut = int(consultaSNMP('CarlosLopez4cv5', ip,  outOID))
        valor = "N:"+ str(trafOut)
        rrdtool.update( ip+ '/out.rrd', valor)
def correrHiloTraficoProtocolo(ip,  ind):
    threads = []
    t = threading.Thread(target=updateTraficoProtocolo, args=(ip, ind))
    t.start()


def generarGraficasTrafico(ip, ventana, filtro):
    tiempoActual = int(time.time())
    tiempoFinal = tiempoActual - 60
    tiempoInicial = tiempoFinal - (60 * int(ventana))
    rrdtool.graph( ip + "/in"+filtro+ ".png",
                     "--start",str(tiempoInicial),
 #                    "--end","N",
                     "--vertical-label="+'Bytes/s'+"",
                     "DEF:in="+ip+"/in.rrd:in:AVERAGE",
                     "DEF:in="+ip+"/in.rrd:in:AVERAGE",
                     "AREA:in#00FF00:in\r")

    rrdtool.graph( ip + "/out"+filtro+ ".png",
                     "--start",str(tiempoInicial),
 #                    "--end","N",
                     "--vertical-label="+'Bytes/s'+"",
                     "DEF:out="+ip+"/out.rrd:out:AVERAGE",
                     "DEF:out="+ip+"/out.rrd:out:AVERAGE",
                     "AREA:out#00FF00:out\r")


def generarGrafica(host, ventana, dato):
    tiempoActual = int(time.time())
    tiempoFinal = tiempoActual - 60
    tiempoInicial = tiempoFinal - (60 * int(ventana))
    rrdtool.graph( host + "/"+dato+ ".png",
                     "--start",str(tiempoInicial),
 #                    "--end","N",
                     "--vertical-label="+'Bytes/s'+"",
                     "DEF:"+dato+"="+host+"/"+dato+".rrd:"+dato+":AVERAGE",
                     "DEF:"+dato+"="+host+"/"+dato+".rrd:"+dato+":AVERAGE",
                     "AREA:"+dato+"#00FF00:"+dato+"\r")


def generarReporte(host, ventana):
    generarGrafica(host, ventana, 'inMCast')
    generarGrafica(host, ventana, 'inPkt')
    generarGrafica(host, ventana, 'rspICMP')
    generarGrafica(host, ventana, 'outSeg')
    generarGrafica(host, ventana, 'inErrDGram')
    time.sleep(25)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="{}".format('inMCast'), ln=1)
    pdf.ln(85)  # move 85 down
    pdf.image(host+'/inMCast.png', x=10, y=8, w=100)

    pdf.cell(200, 10, txt="{}".format('inPkt'), ln=1)
    #pdf.ln(85)  # move 85 down
    pdf.image(host+'/inPkt.png', x=10, y=108, w=100)

    pdf.cell(200, 10, txt="{}".format(host+'rspICMP'), ln=1)
    #pdf.ln(85)  # move 85 down
    pdf.image(host+'/rspICMP.png', x=10, y=208, w=100)
    pdf.add_page()
    pdf.cell(200, 10, txt="{}".format(host+'outSeg'), ln=1)
    #pdf.ln(85)  # move 85 down
    pdf.image(host+'/outSeg.png', x=10, y=308, w=100)

    pdf.cell(200, 10, txt="{}".format(host+'inErrDGram'), ln=1)
    #pdf.ln(85)  # move 85 down
    pdf.image(host+'/inErrDGram.png', x=10, y=408, w=100)

    pdf.output("Reporte de "+ host+".pdf")

opc = 0
while opc != 9:
    print("Selecciona una opción: ")
    print(" 1. Agregar Agente")
    print(" 2. Eliminar Agente")
    print(" 3. Ver Resumen")
    print(" 4. Generar Reporte")
    print(" 5. Mostrar contabilidad de flujo")
    print(" 6. Generar gráficas de tráfico")
    print(" 9. Obtener Datos")
    opc = input()
    if opc == "1":
        print("Introduce la ip: ")
        ip = input()
        print("Introduce la versión de SNMP: ")
        vSNMP = input()
        print("Introduce la comunidad: ")
        comm = input()
        print("Introduce el adaptador a utilizar: ")
        adapt = input()
        agregarUsuario(ip, vSNMP, comm, adapt)
    elif opc == "2":
        i = 0
        ipAux = []
        print("Elige el usuario a eliminar: ")
        with open("agentes.txt", "r") as f:
            lineas = f.readlines()
        for line in lineas:
            print(str(i) + ". " + line.split()[0])
            ipAux.append(line.split()[0])
            i = i+1
        index = int(input())
        eliminarUsuario(ipAux[index])
    elif opc == "3":
        imprimirEstado()
    elif opc == "4":
        ind = 0
        i = 0
        ipAux = []
        print("Elige el usuario para generar el reporte: ")
        with open("agentes.txt", "r") as f:
            lineas = f.readlines()
        for line in lineas:
            print(str(i) + ". " + line.split()[0])
            ipAux.append(line.split()[0])
            i = i+1
        index = int(input())
        ventana = input("De cuántos minutos quieres la ventana?")
        generarReporte(ipAux[index], ventana)
    elif opc == "5":
        i = 0
        ipAux = []
        print("Elige el usuario a contabilizar")
        with open("agentes.txt", "r") as f:
            lineas = f.readlines()
        for line in lineas:
            print(str(i) + ". " + line.split()[0])
            ipAux.append(line.split()[0])
            i = i+1
        print(str(i) + ". otro")
        index = int(input())
        if index != i:
            ip = ipAux[index]
        else:
            ip = input("Introduce la ip del cliente a monitorear: \n")
        print("Ip: " + ip)
        print("¿Qué filtro Deseas aplicar?")
        print(" 0. Interfaz")
        print(" 1. Protocolo")
        print(" 2. Puerto")
        ind = input()
        system("mkdir " + ip)
        crearRRD(ip, 'in')
        crearRRD(ip,'out')
        if ind == "0":

            print("Selecciona la interfaz:")
            output = Popen(['snmpwalk', '-v2c', '-c', 'CarlosLopez4cv5', ip, '1.3.6.1.2.1.2.2.1.2'],stdout=PIPE)
            response = output.communicate()
            pResp = response[0].decode().split('\n')
            del pResp[-1]
            index = 1
            for itf in pResp:
                if ':' in itf:
                    print( '\t' + str(index) + '. ' + itf.split(':')[1])
                    index = index + 1
            numInterfaz = input()
            filtro = pResp[int(numInterfaz)-1].split(':')[1]
            correrHiloTraficoInterfaz(ip, numInterfaz)
        elif ind == "1":
            filtro = 'protocolo'
            print("Elige el protocolo:")
            print(" 0. TCP")
            print(" 1. UDP")
            proto = input()
            filtro = "TCP"
            if proto == '1':
                filtro = "UDP"
            correrHiloTraficoProtocolo(ip, proto)
        elif ind == "2":
            puerto = input("Introduce el puerto:  \n")
        print('Iniciando captura de ' + filtro)
    elif opc == "6":
        ventana = input("Cuál es la ventana para la gráfica?: \n")
        generarGraficasTrafico(ip, int(ventana), filtro)
    elif opc == "9":
        updateTodo()
        #quit()
    else:
        print("Opción no válida")
