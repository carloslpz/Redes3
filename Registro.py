from Agente import Agente
from RRD import RRD
from SNMP import SNMP
from os import system
import subprocess
from pysnmp.hlapi import *
import threading
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import rrdtool
import time
import os

class Registro:
    def __init__(self, nombre = "agentes.txt", agentes = [],
        datos =[['inMCast','1.3.6.1.2.1.31.1.1.1.2.2'],
            ['inPkt','1.3.6.1.2.1.4.9.0'],
            ['rspICMP', '1.3.6.1.2.1.5.21.0'],
            ['outSeg', '1.3.6.1.2.1.6.11.0'],
            ['inErrDGram', '1.3.6.1.2.1.7.3.0']]):
        self.nombre = nombre
        self.agentes = agentes
        self.datos = datos

    def importArch(self, arch = "agentes.txt"):
        with open(arch, "r") as f:
            lineas = f.readlines()
        for line in lineas:
            self.agentes.append(Agente(line.split()[0], line.split()[1], line.split()[2], line.split()[3]))
        return

    def pingUsuario(self, ip):
        res = subprocess.Popen(["ping", "-c", "1" ,ip],stdout = subprocess.PIPE).communicate()[0]
        if b'ttl=' in res:
            return "up"
        else:
            return "down"

    def agregarUsuario(self, agente):
        self.agentes.append(agente)
        f = open(self.nombre, "a+")
        system("mkdir " + agente.ip)
        f.write(agente.ip + ' '+ agente.version+ ' '+ agente.comunidad+ ' '+ agente.interfaz + '\n')
        self.crearTodoRRD(agente.ip)
        f.close()
        return True

    def eliminarUsuario(self, ip):
        #print("Eliminando usuario " + ip)
        with open("agentes.txt", "r") as f:
            lines = f.readlines()
        with open("agentes.txt", "w") as f:
            for line in lines:
                if line.split()[0] != ip:
                    f.write(line)
        for file in os.listdir(ip):
            system("rm " + ip+ "/"+ file)
        system("rmdir " + ip)
        for i,agente in enumerate(self.agentes):
            if agente.ip == ip:
                self.agentes.pop(i)
        return True

    def printUsuarios(self):
        print("\tip\n")
        for i,ag in enumerate(self.agentes):
            print("{}.\t{}\n".format(i, ag.ip))
        return

    def printResumen(self):
        print("#\t ip\t\tversion\tcomunidad\t\tinterfaz\testado\n")
        for i,ag in enumerate(self.agentes):
            ping = self.pingUsuario(ag.ip)
            print("{}.\t {}\t {}\t {}\t {}\t\t{}\n".format(i, ag.ip, ag.version, ag.comunidad, ag.interfaz, ping))
        return

    def crearTodoRRD(self, host):
        for dato in self.datos:
            RRD.crearRRD(host, dato[0])
        return

    def updateTodo(self):
        threads = []
        for agente in self.agentes:
            t = threading.Thread(target=RRD.updateAgente,args=(agente, self.datos))
            threads.append(t)
            t.start()
        return

    def genGrafs(self, ventana):
        for ag in self.agentes:
            for dato in self.datos:
                RRD.generarGrafica(ag, ventana, dato[0])
        return

    def animate(i):
        data = pd.read_csv('data.csv')
        x = data['x_value']
        y1 = data['total_1']
        y2 = data['total_2']

        ax = plt.gca()
        line1, line2 = ax.lines

        line1.set_data(x, y1)
        line2.set_data(x, y2)

        xlim_low, xlim_high = ax.get_xlim()
        ylim_low, ylim_high = ax.get_ylim()

        ax.set_xlim(xlim_low, (x.max() + 5))

        y1max = y1.max()
        y2max = y2.max()
        current_ymax = y1max if (y1max > y2max) else y2max

        y1min = y1.min()
        y2min = y2.min()
        current_ymin = y1min if (y1min < y2min) else y2min

        ax.set_ylim((current_ymin - 5), (current_ymax + 5))
        return


    def grafTiempoReal(self, agente, dato):
            plt.style.use('fivethirtyeight')
            x_vals = []
            y_vals = []
            index = count()
            plt.plot([], [], label='Channel 1')
            plt.plot([], [], label='Channel 2')
            ani = FuncAnimation(plt.gcf(), self.animate, interval=1000)
            plt.legend()
            plt.tight_layout()
            plt.show()
