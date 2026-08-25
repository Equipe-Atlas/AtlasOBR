from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Direction, Color, Stop
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.system.set_stop_button(None)

sensor_garra = ColorSensor(Port.F)
sensor_garra.detectable_colors([
    Color.SILVER,
    Color.BLACK,
    Color.WHITE,
    Color.NONE,
    Color.RED,
])
us_direito = UltrasonicSensor(Port.D)
us_esquerdo = UltrasonicSensor(Port.B)
motor_garra = Motor(Port.E)
motor_selecao = Motor(Port.C)
motor_descarte = Motor(Port.A)

ANG_GARRA_ABERTA = 0
ANG_GARRA_FECHADA = 120
ANG_GARRA_LEVANTADA = 180
ANG_SELECAO_CENTRO = 0
ANG_SELECAO_VIVA = -45
ANG_SELECAO_MORTA = 45
ANG_DESCARTE_FECHADO = 0
ANG_DESCARTE_ABERTO = 90
LIM_PRATA_VITIMA = 80
LIM_ESCURA_VITIMA = 20

CMD_IDLE = 0
CMD_PICKUP = 1
CMD_RELEASE = 2
CMD_PADDLE_ALIVE = 3
CMD_PADDLE_DEAD = 4
CMD_DISPOSAL_CLOSE = 5
CMD_DISPOSAL_OPEN = 6
CMD_RESCUE_MODE = 7
CMD_TRANSPORT_MODE = 8
CMD_STOP = 9
STAT_READY = 0
STAT_PICKUP_DONE = 1
STAT_RELEASE_DONE = 2
STAT_VITIMA_VIVA = 3
STAT_VITIMA_MORTA = 4
STAT_SEM_VITIMA = 5
STAT_OCUPADO = 6

status_atual = STAT_READY
ultimo_cmd_recebido = CMD_IDLE

def ler_comando():
    return hub.ble.observe(1)

def enviar_dados(us_e, us_d, cor, status):
    hub.ble.broadcast((us_e, us_d, cor, status))
def abrir_garra():
    motor_garra.run_target(200, ANG_GARRA_ABERTA, Stop.HOLD)
    wait(200)

def fechar_garra():
    angulo_stall = motor_garra.run_until_stalled(300, Stop.HOLD, duty_limit=40)
    wait(300)
    return angulo_stall

def levantar_garra():
    motor_garra.run_target(200, ANG_GARRA_LEVANTADA, Stop.HOLD)
    wait(300)

def soltar_vitima():
    motor_garra.run_target(200, ANG_GARRA_ABERTA, Stop.HOLD)
    wait(300)

def identificar_vitima():
    leituras = []
    for i in range(5):
        leituras.append(sensor_garra.reflection())
        wait(50)
    media = sum(leituras) / len(leituras)
    if media > LIM_PRATA_VITIMA:
        return STAT_VITIMA_VIVA
    elif media < LIM_ESCURA_VITIMA:
        return STAT_VITIMA_MORTA
    else:
        cor = sensor_garra.color()
        if cor == Color.SILVER:
            return STAT_VITIMA_VIVA
        elif cor == Color.BLACK:
            return STAT_VITIMA_MORTA
        else:
            return STAT_SEM_VITIMA

def palheta_selecao_centro():
    motor_selecao.run_target(150, ANG_SELECAO_CENTRO, Stop.HOLD)
    wait(200)
def palheta_selecao_viva():
    motor_selecao.run_target(150, ANG_SELECAO_VIVA, Stop.HOLD)
    wait(200)
def palheta_selecao_morta():
    motor_selecao.run_target(150, ANG_SELECAO_MORTA, Stop.HOLD)
    wait(200)
def palheta_descarte_fechar():
    motor_descarte.run_target(150, ANG_DESCARTE_FECHADO, Stop.HOLD)
    wait(300)
def palheta_descarte_abrir():
    motor_descarte.run_target(150, ANG_DESCARTE_ABERTO, Stop.HOLD)
    wait(300)

def rotina_coleta():
    global status_atual
    status_atual = STAT_OCUPADO
    abrir_garra()
    angulo_antes = motor_garra.angle()
    angulo_stall = fechar_garra()
    deslocamento = abs(angulo_stall - angulo_antes)
    if deslocamento < 10:
        abrir_garra()
        status_atual = STAT_SEM_VITIMA
        return
    resultado = identificar_vitima()
    if resultado == STAT_SEM_VITIMA:
        abrir_garra()
        status_atual = STAT_SEM_VITIMA
        return
    levantar_garra()
    if resultado == STAT_VITIMA_VIVA:
        palheta_selecao_viva()
    else:
        palheta_selecao_morta()

    status_atual = resultado

def rotina_resgate_mode():
    global status_atual
    palheta_descarte_fechar()
    palheta_selecao_centro()
    abrir_garra()
    status_atual = STAT_READY
def rotina_transport_mode():
    global status_atual
    palheta_descarte_fechar()
    levantar_garra()
    status_atual = STAT_READY

def rotina_stop():
    global status_atual
    motor_garra.stop()
    motor_selecao.stop()
    motor_descarte.stop()
    status_atual = STAT_READY

def processar_comando(cmd, param=0):
    global status_atual
    if cmd == CMD_PICKUP:
        rotina_coleta()
    elif cmd == CMD_RELEASE:
        soltar_vitima()
        status_atual = STAT_RELEASE_DONE
    elif cmd == CMD_PADDLE_ALIVE:
        palheta_selecao_viva()
        status_atual = STAT_READY
    elif cmd == CMD_PADDLE_DEAD:
        palheta_selecao_morta()
        status_atual = STAT_READY
    elif cmd == CMD_DISPOSAL_CLOSE:
        palheta_descarte_fechar()
        status_atual = STAT_READY
    elif cmd == CMD_DISPOSAL_OPEN:
        palheta_descarte_abrir()
        status_atual = STAT_READY
    elif cmd == CMD_RESCUE_MODE:
        rotina_resgate_mode()
    elif cmd == CMD_TRANSPORT_MODE:
        rotina_transport_mode()
    elif cmd == CMD_STOP:
        rotina_stop()
    elif cmd == CMD_IDLE:
        pass

def main():
    global status_atual, ultimo_cmd_recebido
    hub.display.text("INI")
    motor_garra.run_target(200, ANG_GARRA_LEVANTADA, Stop.HOLD)
    motor_selecao.run_target(150, ANG_SELECAO_CENTRO, Stop.HOLD)
    motor_descarte.run_target(150, ANG_DESCARTE_FECHADO, Stop.HOLD)
    wait(500)
    status_atual = STAT_READY
    hub.display.text("RDY")
    timer_broadcast = StopWatch()
    while True:
        cmd_recebido = ler_comando()
        if cmd_recebido is not None:
            if isinstance(cmd_recebido, tuple) and len(cmd_recebido) >= 1:
                cmd = cmd_recebido[0]
                param = cmd_recebido[1] if len(cmd_recebido) > 1 else 0
            else:
                cmd = cmd_recebido
                param = 0

            if cmd != ultimo_cmd_recebido:
                ultimo_cmd_recebido = cmd
                if cmd != CMD_IDLE:
                    processar_comando(cmd, param)
        if timer_broadcast.time() >= 100:
            us_e = us_esquerdo.distance()
            us_d = us_direito.distance()
            cor = sensor_garra.reflection()
            enviar_dados(us_e, us_d, cor, status_atual)
            timer_broadcast.reset()
        wait(20)
main()