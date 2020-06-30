import dns.resolver
import time

class SensorDNS:
    def __init__(self, agente):
        self.agente = agente

    #Mandar a llamar site con la página a buscar:
    #zona.carloslopez4cm3.com

    ##  Obtener tiempo de respuesta EN MILISEGUNDOS
    def getTiempoResp(self, site):
        agSolver = dns.resolver.Resolver()
        #Timeot de 4 segundos
        agSolver.timeout = 4
        agSolver.lifetime = 4
        agSolver.nameservers = [self.agente.ip]
        start = time.time()
        try:
            query = agSolver.query(site , 'A')
            return (time.time() - start)*1000
        except:
            return 0

    def getStatus(self, site):
        agSolver = dns.resolver.Resolver()
        #Timeot de 4 segundos
        agSolver.timeout = 4
        agSolver.lifetime = 4
        agSolver.nameservers = [self.agente.ip]
        try:
            query = agSolver.query(site , 'A')
            return 'Up'
        except:
            return 'Down'
