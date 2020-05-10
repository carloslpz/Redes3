from os import system
import telnetlib
import ftplib
from pysnmp.hlapi import *
from subprocess import Popen, PIPE

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

def agregarUsuario(ip, vSNMP, comm, adapt):
    #time.tzset()
    f = open("agentes.txt", "a+")
    system("mkdir " + ip)
    f.write(ip + ' '+ vSNMP+ ' '+ comm+ ' '+ adapt +'\n')
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

def generarConfInd(ip):
    with telnetlib.Telnet(ip) as tn:
        tn.read_until(b"User: ")
        tn.write('rcp'.encode('ascii') + b"\n")
        tn.read_until(b"Password: ")
        tn.write('rcp'.encode('ascii') + b"\n")
        tn.write(b"enable\r")
        tn.write('copy run start'.encode('ascii') + b"\r")
        tn.write(b"exit\r")
        tn.write(b"exit\r")
        tn.read_all()
        print('Configuración de {} actualizada'.format(ip))

def generarArchConf():
    ips = []
    with open("agentes.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            ips.append(line.split()[0])
        for ip in ips:
                generarConfInd(ip)
    return

def extraerArchConf(ip):
    with ftplib.FTP(ip) as ftp:
        ftp.login('rcp', 'rcp')
        ftp.retrbinary('RETR startup-config', open(ip+'/startup-config', 'wb').write)
        print('Archivo de configuracion guardado en {}\n'.format(ip))
        ftp.quit()
        return

def enviarArchConf(origen, destino):
    with ftplib.FTP(destino) as ftp:
        ftp.login('rcp', 'rcp')
        #extraerArchConf(origen)
        archOrigen = open(origen +'/startup-config','rb')
        ftp.storbinary('STOR startup-config', archOrigen)
        print('Archivo de {} subido a {}\n'.format(origen, destino))
        ftp.quit()
        return

def genReporteGeneral():
    ips = []
    with open("agentes.txt", "r") as f:
        lines = f.readlines()
        with open("reporte.txt", 'w') as r:
            for line in lines:
                ips.append(line.split()[0])
                for numAg,ip in enumerate(ips):
                    r.write('{}. {}\n'.format(numAg, ip))
                    r.write('\t' + str(consultaSNMP('CarlosLopez4cv5', ip, '1.3.6.1.2.1.1.1.0')))
                    r.write('\t' + 'SystemuUpTime: {}\n'.format(consultaSNMP('CarlosLopez4cv5', ip, '1.3.6.1.2.1.1.1.0')))
                    r.write('\t' + 'RAM Disponible: {}\n'.format(consultaSNMP('CarlosLopez4cv5', ip,'1.3.6.1.4.1.2021.4.5.0')))
                    r.write('\t' + 'Carga de CPU en 15 minutos: {}\n'.format(consultaSNMP('CarlosLopez4cv5', ip,'1.3.6.1.4.1.2021.10.1.3.3')))
                    r.write('\t' + 'Interfaces: \n')
                    output = Popen(['snmpwalk', '-v2c', '-c', 'CarlosLopez4cv5', ip, '1.3.6.1.2.1.2.2.1.2'],stdout=PIPE)
                    response = output.communicate()
                    interfaces = response[0].decode().split('\n')
                    del interfaces[-1]
                    for itf in interfaces:
                        r.write('\t' + '\t' + str(itf.split(':')[1]) + '\n')
    return

def printAgentes():
    with open("agentes.txt", "r") as f:
        lineas = f.readlines()
    for i,line in enumerate(lineas):
        print(str(i) + ". " + line.split()[0])
    return

def indexToIp(index):
    with open("agentes.txt", "r") as f:
        lineas = f.readlines()
    return str(lineas[int(index)]).split()[0]

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

printAgentes()
opc = 's'
while opc == 's':
    opc = input("¿Deseas añadir nuevos agentes?: (s/n)\n")
    if opc == 's':
        ip = input("Introduce la ip: \n")
        agregarUsuario(ip, 'v1', 'CarlosLopez4cv5', 'tap0')
        print("Agente agregado")
    else:
        print("trabajando con los agentes: \n")
        printAgentes()
        print("\n\n\n")

opc = 1
while opc != 9:
    print("1. Generar archivos de configuracion")
    print("2. Extraer archivo de configuración")
    print("3. Enviar archivo de configuración")
    print("4. Generar reporte")

    opc = input()
    if opc == '1':
        generarArchConf()
    elif opc == '2':
        printAgentes()
        ipIndex = input()
        extraerArchConf(indexToIp(ipIndex))
    elif opc == '3':
        print("¿De qué agente deseas obtener la configuracion?\n")
        printAgentes()
        origen = input()
        print("¿A qué agente quieres subir la configuración?\n")
        destino = input()
        enviarArchConf(indexToIp(origen), indexToIp(destino))
    elif opc == '4':
        genReporteGeneral()
    elif opc == '9':
        preint("Goodbye\n")
