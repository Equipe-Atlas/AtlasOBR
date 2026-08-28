from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port, Stop
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])

COD_ENTROU_RESGATE = 200
COD_CENTRALIZADO   = 400
COD_PARA           = 301
COD_FRENTE         = 302
COD_DIREITA        = 303
COD_ESQUERDA       = 304
COD_FIM            = 600

LIMIAR_CANTO = 150
LIMIAR_PAREDE = 90
MAX_VITIMAS = 6
TEMPO_MAX_BUSCA_MS = 90000
OFFSET_IMU = 3.6

VEL_GARRA = 300
ANGULO_GARRA_COLETA = 120
ANGULO_SELECAO = 45
ANGULO_DESCARTE = 100

cor_vitima = ColorSensor(Port.F)
ultra_esq = UltrasonicSensor(Port.B)
ultra_dir = UltrasonicSensor(Port.D)
garra = Motor(Port.E)
selecao = Motor(Port.C)
descarte = Motor(Port.A)

Color.SILVER = Color(h=0, s=0, v=75)
Color.BLACK = Color(h=240, s=100, v=20)
cor_vitima.detectable_colors((Color.SILVER, Color.BLACK, Color.WHITE, Color.NONE))

def calibrar_garra():
    garra.run_until_stalled(-200, then=Stop.HOLD, duty_limit=40)
    garra.reset_angle(0)

def e_vitima_viva():
    dados = cor_vitima.hsv()
    return dados.s < 20 and dados.v > 55

def e_vitima_morta():
    dados = cor_vitima.hsv()
    return dados.v < 20

def leitura_confirmada(funcao_teste, tentativas=3, intervalo_ms=15):
    acertos = 0
    for _ in range(tentativas):
        if funcao_teste():
            acertos += 1
        wait(intervalo_ms)
    return acertos >= (tentativas - 1)

def coletar_vitima(viva):
    angulo = ANGULO_SELECAO if viva else -ANGULO_SELECAO
    selecao.run_angle(200, angulo)
    wait(150)
    garra.run_angle(VEL_GARRA, ANGULO_GARRA_COLETA)
    wait(200)
    garra.run_angle(VEL_GARRA, -ANGULO_GARRA_COLETA)
    wait(150)
    selecao.run_angle(200, -angulo)
    wait(150)

def descartar_vitimas():
    descarte.run_angle(150, ANGULO_DESCARTE)
    wait(500)
    descarte.run_angle(150, -ANGULO_DESCARTE)
    wait(200)

def leitura_imu_nivelada():
    arfagem, rolagem = hub.imu.tilt()
    arfagem = arfagem + OFFSET_IMU
    return -3 < arfagem < 3

hub.light.on(Color.MAGENTA)
calibrar_garra()

estado = "espera"
vitimas_coletadas = 0
vitimas_vivas = 0
vitimas_mortas = 0
cronometro_busca = StopWatch()

while True:
    dist_esq = ultra_esq.distance()
    dist_dir = ultra_dir.distance()

    if estado == "espera":
        if dist_esq < LIMIAR_CANTO and dist_dir < LIMIAR_CANTO and leitura_imu_nivelada():
            print("Atlas: entrando na area de resgate")
            hub.ble.broadcast(COD_ENTROU_RESGATE)
            hub.light.on(Color.YELLOW)
            estado = "aguarda_centralizacao"

    elif estado == "aguarda_centralizacao":
        msg = hub.ble.observe(1)
        if msg is None:
            msg = 0
        hub.ble.broadcast(COD_ENTROU_RESGATE)
        if msg == COD_CENTRALIZADO:
            print("Atlas: area centralizada, iniciando busca")
            hub.light.on(Color.CYAN)
            cronometro_busca.reset()
            estado = "busca"

    elif estado == "busca":
        if e_vitima_viva() or e_vitima_morta():
            hub.ble.broadcast(COD_PARA)
            wait(300)
            estado = "identifica"
        elif cronometro_busca.time() > TEMPO_MAX_BUSCA_MS:
            print("Atlas: tempo de busca esgotado")
            estado = "finaliza"
        elif dist_esq < LIMIAR_PAREDE:
            hub.ble.broadcast(COD_DIREITA)
        elif dist_dir < LIMIAR_PAREDE:
            hub.ble.broadcast(COD_ESQUERDA)
        else:
            hub.ble.broadcast(COD_FRENTE)

    elif estado == "identifica":
        hub.ble.broadcast(COD_PARA)
        if leitura_confirmada(e_vitima_viva):
            print("Atlas: vitima viva (prata)")
            estado = "coleta_viva"
        elif leitura_confirmada(e_vitima_morta):
            print("Atlas: vitima morta (preta)")
            estado = "coleta_morta"
        else:
            print("Atlas: leitura falsa, voltando a buscar")
            estado = "busca"

    elif estado == "coleta_viva" or estado == "coleta_morta":
        hub.ble.broadcast(COD_PARA)
        coletar_vitima(viva=(estado == "coleta_viva"))
        vitimas_coletadas += 1
        if estado == "coleta_viva":
            vitimas_vivas += 1
        else:
            vitimas_mortas += 1
        print("Vitimas coletadas: {} (vivas: {}, mortas: {})".format(
            vitimas_coletadas, vitimas_vivas, vitimas_mortas))
        if vitimas_coletadas >= MAX_VITIMAS:
            estado = "finaliza"
        else:
            cronometro_busca.reset()
            estado = "busca"

    elif estado == "finaliza":
        hub.light.on(Color.RED)
        descartar_vitimas()
        estado = "concluido"

    elif estado == "concluido":
        hub.ble.broadcast(COD_FIM)

    wait(20)