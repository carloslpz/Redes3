from Agente import Agente
from Registro import Registro
from os import system, path

###COMANDOS PARA INICIAR SERVIDORES:
###     FTP:
###     sudo systemctl restart vsftpd
###     HTTP:
###     cd /opt/lampp
###     sudo ./manager-linux-x64.run
###     DNS:
###     sudo service bind9 restart
###     SMTP:
###     sudo /etc/init.d/postfix start
###     SensorSSH
###     sudo service ssh start



def printMenu():
    print("1. Recuperar Datos SNMP\n")
    print("2. Generar Gráficas\n")
ag = Agente('127.0.0.1', 'v1', 'CarlosLopez4cv5', 'wlp3s0')

#Datos SNMP
datos = []
datos.append(['CPUPercUser', '1.3.6.1.4.1.2021.11.9.0'])
datos.append(['RAMUsd','1.3.6.1.4.1.2021.4.6.0'])
datos.append(['HDDUsdPerc','1.3.6.1.4.1.2021.9.1.9.1'])
#Creación del Registro
reg = Registro()
reg.datos = datos
if path.exists("agentes.txt"):
    reg.agregarUsuario(ag)
else:
    reg.importArch()

opc = 0

while(opc != 3):
    printMenu()
    opc = int(input())
    if opc == 1:
        system('clear')
        print("Recuperando datos:")
        reg.updateTodo()
    elif opc == 2:
        system('clear')
        print("Generando gráficas")
        reg.genGrafs(20)
    elif opc == 3:
        system('clear')
        print("Tomando pruebas de servidores: \n")
        pruebasEstres()

    else:
        system('clear')
        print("Opción {} inválida\n\n".format(opc))
