from os import system
from pysnmp.hlapi import *
import os
import rrdtool
import time
import threading
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
        print("\t\t\t" + agente)
        print("Estado del agente: ")
        if ping(agente) == 0:
            print("up")
        else:
            print("down")
        print("Número de interfaces:")
        print(consultaSNMP(comunidad[i], agente[i], '1.3.6.1.2.1.2.1.0'))
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

opc = 0
while opc != 9:
    print("Selecciona una opción: ")
    print(" 1. Agregar Agente")
    print(" 2. Eliminar Agente")
    print(" 3. Ver Resumen")
    print(" 4. Generar Reporte")
    print(" 9. Salir")
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

    elif opc == "9":
        updateTodo()
        #quit()
    else:
        print("Opción no válida")
