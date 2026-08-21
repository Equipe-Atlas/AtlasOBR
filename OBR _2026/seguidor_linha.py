from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port, Direction
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

CANAL_PROMETEU = 1
CANAL_ATLAS = 2

hub = PrimeHub(broadcast_channel=CANAL_PROMETEU,observe_channels=[CANAL_ATLAS])

motor_esq = Motor(Port.F,positive_direction=Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.E)

sensor_esq = ColorSensor(Port.B)
sensor_dir = ColorSensor(Port.D)
sensor_meio = ColorSensor(Port.A)
ultra = UltrasonicSensor(Port.C)

andar = DriveBase(
    motor_esq,
    motor_dir,
    63,
    133
)
andar.settings(
    straight_speed=100,
    straight_acceleration=300,
    turn_rate=100,
    turn_acceleration=300
)


V_PRETO = 15
V_PRATA = 77
V_BRANCO = 100
TOL_PRATA = 18
CONFIRMACOES_PRATA = 4
REFLEXAO = 36
VEL = 150
KP = 4
KI = 0.05
KD = 20
integral = 0
erro_anterior = 0
contador_prata = 0
sequencia = 0
ultima_sequencia = -1
estado = "LINHA"

timer_comunicacao = StopWatch()
def enviar(tipo, valor=0):
    global sequencia

    sequencia += 1
    hub.ble.broadcast((tipo, valor, sequencia))


def receber():
    global ultima_sequencia
    msg = hub.ble.observe(CANAL_ATLAS)
    if msg is None:
        return None
    if len(msg) >= 3:
        if msg[2] <= ultima_sequencia:
            return None
        ultima_sequencia = msg[2]
    return msg

def e_prata(sensor):
    h, s, v = sensor.hsv()
    if s > 20:
        return False
    dp = abs(v - V_PRETO)
    ds = abs(v - V_PRATA)
    db = abs(v - V_BRANCO)
    return ds <= TOL_PRATA and ds < dp and ds < db

def detecta_prata():
    global contador_prata
    quantidade = 0
    if e_prata(sensor_esq):
        quantidade += 1
    if e_prata(sensor_meio):
        quantidade += 1
    if e_prata(sensor_dir):
        quantidade += 1
    if quantidade >= 2:
        contador_prata += 1
    else:
        contador_prata = 0
    if contador_prata >= CONFIRMACOES_PRATA:

        contador_prata = 0
        return True

    return False

def seguir_linha():
    global integral
    global erro_anterior
    meio = sensor_meio.reflection()
    erro = REFLEXAO - meio
    integral += erro
    if integral > 100:
        integral = 100
    if integral < -100:
        integral = -100
    derivada = erro - erro_anterior
    correcao = (
        KP * erro
        +
        KI * integral
        +
        KD * derivada
    )
    if correcao > 300:
        correcao = 300
    if correcao < -300:
        correcao = -300
    motor_esq.run(VEL + correcao)
    motor_dir.run(VEL - correcao)
    erro_anterior = erro


def enviar_ultra():
    if timer_comunicacao.time() < 100:
        return
    distancia = ultra.distance()
    if distancia > 2000:
        distancia = 2000
    enviar("U", distancia)
    timer_comunicacao.reset()

hub.imu.reset_heading(0)
hub.light.on(Color.BLUE)
enviar("BOOT", 1)
while True:
    msg = receber()
    if msg is not None:
        evento = msg[0]
        if evento == "OK":
            estado = "RESGATE"
        elif evento == "FALHA":
            estado = "LINHA"
        elif evento == "CONTINUE":
            estado = "LINHA"
        elif evento == "FINAL":
            estado = "LINHA"
    enviar_ultra()

    if estado == "LINHA":
        seguir_linha()
        if detecta_prata():
            andar.stop()
            enviar("PRATA", 1)
            estado = "ESPERANDO"

    elif estado == "ESPERANDO":
        andar.stop()
        enviar_ultra()

    elif estado == "RESGATE":
        andar.stop()
        enviar("RESGATE", 1)
    wait(10) 