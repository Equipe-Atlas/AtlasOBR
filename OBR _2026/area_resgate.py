from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port, Direction
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.light.on(Color.MAGENTA)

cores = ColorSensor(Port.F)
ultra_esq = UltrasonicSensor(Port.B)
ultra_dir = UltrasonicSensor(Port.D)
garra = Motor(Port.E, reset_angle=False)
selecao = Motor(Port.C)
descarte = Motor(Port.A)

omnitrix = StopWatch()

dsaida = 100
PASSO_QUADRADO = 200
TEMPO_PASSO = 2500
TEMPO_GIRO = 1200
GARRA_CIMA = 0
GARRA_BAIXO = -90
COD_ENTROU_CANTO = 100
COD_SAIDA_ESQ = 201
COD_SAIDA_FRENTE = 202
COD_SAIDA_DIR = 203
COD_PRECISA_GIRAR = 209
COD_LIBERA = 10000
COD_ANDA_FRENTE = 300
COD_GIRA_90 = 301
COD_ALINHA = 401

parar = 0

Color.SILVER = Color(h=0, s=0, v=75)
Color.BLACK = Color(h=240, s=100, v=50)
Color.WHITE = Color(h=0, s=0, v=100)
Color.GREEN = Color(h=186, s=80, v=50)
Color.RED = Color(h=0, s=100, v=50)
cores_ler = (Color.SILVER, Color.BLACK, Color.WHITE, Color.GREEN, Color.RED)
cores.detectable_colors(cores_ler)
hsv = cores.hsv()
def reseta_angulo():
    garra.run_target(300)
    wait(200)
    garra.reset_angle(0)
    wait(200)

garra.run_target(500, 0)
while True:
    dist_esq = ultra_esq.distance()
    dist_dir = ultra_dir.distance()
    arfagem, rolagem = hub.imu.tilt()
    arfagem = arfagem + 3.6
    mensagem = hub.ble.observe(1)
    if mensagem is None:
        mensagem = 0
    print(mensagem)
    if dist_esq + dist_dir < 300 and arfagem > -3 and arfagem < 3:
        vez = 1
        garra.run(-670)
        hub.ble.broadcast(200)
        wait(1000)
        hub.imu.reset_heading(0)
        dist_esq = ultra_esq.distance()
        dist_dir = ultra_dir.distance()
        if dist_esq < dist_dir:
            hub.ble.broadcast(502)
            parede = 502
        else:
            hub.ble.broadcast(503)
            parede = 503
        wait(1000)
        garra.stop()
        while parar != 7777777:
            while vez != 3:
                if parede == 502:
                    wait(20)
                elif parede == 503:
                    while hub.imu.heading() > -10:
                        dist_esq = ultra_esq.distance()
                        dist_dir = ultra_dir.distance()
                        dist = (dist_esq, dist_dir)
                        hub.ble.broadcast(dist)
                        wait(20)
                    hub.imu.reset_heading(0)
                    wait(2000)
                    dist_dir = ultra_dir.distance()
                    if dist_dir < 150: canto = 1
                    else: canto = 0
                    print(canto)
                    hub.ble.broadcast(canto)
                    print(dist_dir)
                    hub.light.on(Color.GREEN)
                    if canto == 1: 
                        while hub.imu.heading() < 69: wait(20)
                        while cores.color() != Color.GREEN and cores.color() != Color.RED:
                            cor = cores.color() 
                            hub.ble.broadcast(str(cor))
                            print("cor:", cor, "| h:", hsv.h, "s:", hsv.s, "v:", hsv.v)
                            if cor == Color.GREEN:
                                canto_verde = (parede, vez, cor)
                            elif cor == Color.GREEN:
                                canto_vermelho = (parede, vez, cor)
                            wait(20)
                vez = vez + 1
                wait(20)

    wait(20)