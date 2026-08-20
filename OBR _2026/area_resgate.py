from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port
from pybricks.tools import wait


CANAL_PROMETEU = 1
CANAL_ATLAS = 2

hub = PrimeHub(broadcast_channel=CANAL_ATLAS,observe_channels=[CANAL_PROMETEU])

sensor_cor = ColorSensor(Port.F)
ultra_esq = UltrasonicSensor(Port.B)
ultra_dir = UltrasonicSensor(Port.D)

garra = Motor(Port.E)
selecao = Motor(Port.C)
descarte = Motor(Port.A)

V_PRETO = 15
V_PRATA = 77
V_BRANCO = 100
TOL_PRATA = 18
ultra_prometeu = 2000
sequencia = 0
ultima_sequencia = -1
estado = "ESPERANDO"

def enviar(tipo, valor=0):
    global sequencia
    sequencia += 1
    hub.ble.broadcast((tipo, valor, sequencia))

def receber():
    global ultima_sequencia
    global ultra_prometeu

    msg = hub.ble.observe(CANAL_PROMETEU)

    if msg is None:
        return None
    if len(msg) >= 3:
        if msg[2] <= ultima_sequencia:
            return None
        ultima_sequencia = msg[2]
    if msg[0] == "U":
        ultra_prometeu = msg[1]
    return msg

def e_prata():
    h, s, v = sensor_cor.hsv()
    if s > 20:
        return False
    dp = abs(v - V_PRETO)
    ds = abs(v - V_PRATA)
    db = abs(v - V_BRANCO)
    return ds <= TOL_PRATA and ds < dp and ds < db

def confirma_prata():
    pontos = 0
    for _ in range(5):
        if e_prata():
            pontos += 1
        wait(10)
    return pontos >= 3

def ler_ultra(sensor):
    total = 0
    for _ in range(3):
        v = sensor.distance()
        if v > 2000:
            v = 2000
        total += v
        wait(10)
    return total // 3

def ambiente():
    esq = ler_ultra(ultra_esq)
    dire = ler_ultra(ultra_dir)
    frente = ultra_prometeu
    return esq, frente, dire

def confirmar_area():
    esq, frente, dire = ambiente()
    pontos = 0
    if confirma_prata():
        pontos += 2
    if esq < 300:
        pontos += 1
    if dire < 300:
        pontos += 1
    if frente < 300:
        pontos += 1
    print("E:", esq, "F:", frente, "D:", dire, "P:", pontos)
    return pontos >= 3

def pegar():
    garra.run(250)
    while True:
        if garra.angle() >= 0:
            break
        wait(10)
    garra.stop()

def soltar():
    garra.run(-250)
    while True:
        if garra.angle() <= -360:
            break
        wait(10)
    garra.stop()

def selecionar():
    selecao.run_angle(300, 180, wait=True)

def descartar():
    descarte.run_angle(300, 90, wait=True)

def executar_resgate():
    enviar("RESGATE", 1)
    pegar()
    selecionar()
    descartar()
    soltar()
    enviar("FINAL", 1)

hub.light.on(Color.RED)

enviar("BOOT", 1)

while True:
    dist_dir = ultra_dir.distance()
    dist_esq = ultra_esq.distance()
    if dist_esq < dist_dir:
        enviar(dist_esq)
    else:
        enviar(dist_dir)
    msg = receber()
    if estado == "ESPERANDO":
        if msg is not None and msg[0] == "PRATA":
            estado = "CONFIRMANDO"

    elif estado == "CONFIRMANDO":
        if confirmar_area():
            enviar("OK", 1)
            estado = "RESGATE"
        else:
            enviar("FALHA", 0)
            estado = "ESPERANDO"

    elif estado == "RESGATE":

        executar_resgate()
        estado = "FINAL"

    elif estado == "FINAL":
        enviar("FINAL", 1)
        wait(100)
    wait(10)
    #meu deus