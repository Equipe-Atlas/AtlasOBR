from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Direction, Color, Button, Stop
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

hub = PrimeHub(broadcast_channel=1, observe_channels=[2]) 

motor_esq = Motor(Port.F, Direction.COUNTERCLOCKWISE)
motor_dir = Motor(Port.E, Direction.CLOCKWISE)
sensor_esq = ColorSensor(Port.B)
sensor_meio = ColorSensor(Port.A)
sensor_dir = ColorSensor(Port.D)
us_frontal = UltrasonicSensor(Port.C)

robo = DriveBase(motor_esq, motor_dir, wheel_diameter=63, axle_track=133)
robo.use_gyro(True)

KP = 1.2
KI = 0.0
KD = 0.8
VEL_PADRAO = 180
VEL_CURVA = 100
VEL_RESGATE = 80
VEL_BUSCA = 60
LIM_PRETO = 15
LIM_BRANCO = 55
LIM_PRATA = 88
DIST_OBSTACULO = 60
DIST_PAREDE = 80
DIST_VITIMA = 40
TEMPO_MAXIMO = 290000

pid_integral = 0
pid_ultimo_erro = 0
alvo_pid = 35

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
STAT_RELASE_DONE = 2
STAT_VITIMA_VIVA = 3
STAT_VITIMA_MORTA = 4
STAT_SEM_VITIMA = 5
STAT_OCUPADO = 6

def enviar_comando(cmd, param=0):
      hub.ble.broadcast((cmd, param))
def ler_dados_atlas():
      return hub.ble.observe(2)
def obter_status_atlas():
      dados = ler_dados_atlas()
      if dados is not None and len(dados) >= 4:
            return dados[2]
      return None
def aguardar_status(status_esperando, timeout_ms=5000):
      timer = StopWatch()
      while timer.time() < timeout_ms:
            s = obter_status_atlas()
            if s == status_esperando:
                  return True
            wait(50)
      return False
def na_linha(s):
      return s.reflection() < LIM_PRETO
def no_branco(s):
      return s.reflection() > LIM_BRANCO
def eh_prata(s):
      return s.reflection() > LIM_PRATA
def eh_vermelho(s):
      return s.color() == Color.RED
def todos_pretos():
      return na_linha(sensor_esq) and na_linha(sensor_meio) and na_linha(sensor_dir)
def todos_brancos():
      return no_branco(sensor_esq) and no_branco(sensor_meio) and no_branco(sensor_dir)
def calibrar():
      global alvo_pid
      hub.display.text("IMU")
      timer_imu = StopWatch()
      while not hub.imu.ready() and timer_imu.time() < 5000:
            wait(100)
      if hub.imu.ready():
            hub.display.text("OK")
      else:
            hub.display.text("!")
      wait(500)
      hub.display.text("PRE")
      while not hub.buttons.pressed():
            wait(10)
      while hub.buttons.pressed():
            wait(10)
      preto = sensor_meio.reflection()
      hub.display.text("BRC")
      while not hub.buttons.pressed():
            wait(10)
      while hub.buttons.pressed():
            wait(10)
      branco = sensor_meio.reflection()
      alvo_pid = (preto + branco) / 2
      robo.settings(straight_speed=200, turn_rate=120)
      hub.display.text("GO")
      wait(500)
def reset_pid():
      global pid_integral, pid_ultimo_erro
      pid_integral = 0
      pid_ultimo_erro = 0
def seguir_linha(velocidade=VEL_PADRAO):
      global pid_integral, pid_ultimo_erro
      refl = sensor_meio.reflection()
      erro = alvo_pid - refl
      pid_integral += erro
      pid_integral = max(-50, min(50, pid_integral))
      derivativo = erro - pid_ultimo_erro
      pid_ultimo_erro = erro
      correcao = KP * erro + KI * pid_integral + KD * derivativo
      robo.drive(velocidade, correcao)

      if us_frontal.distance() < DIST_OBSTACULO:
            return "obstaculo"
      if eh_prata(sensor_meio):
            return "prata"
      if eh_vermelho(sensor_meio):
            return "vermelho"
      if todos_pretos():
            return "intersecao"
      if todos_brancos():
            return "perdeu_linha"
      return None

def desviar_obstaculo():
      robo.stop()
      wait(100)
      if dist < 90:
                robo.turn(80)
                ultimo_dist = us_frontal.distance()
                while dist <= ultimo_dist:
                    ultimo_dist = us_frontal.distance()
                    motor_esq.run(-100)
                    motor_dir.run(100)
                    wait(20)
                    dist = us_frontal.distance()
                    if dist > 300: dist = 300
                    if ultimo_dist > 300: ultimo_dist = 300
                    if dist > (ultimo_dist + 1): dist = ultimo_dist
                    print("distância: {}, ultima: {}".format(dist, ultimo_dist))
                robo.turn(100)
                robo.straight(200)
                robo.turn(-100)
                robo.straight(400)
                robo.turn(-100)
                robo.straight(200)
                robo.turn(-115)
                motor_esq.run(100)
                motor_dir.run(100)
                wait(2500)
      timer  = StopWatch()
      while timer.time() < 2000:
            if na_linha(sensor_meio) or na_linha(sensor_esq) or na_linha(sensor_dir):
                  reset_pid()
                  return
            robo.drive(VEL_BUSCA, -30)
            wait(10)
      robo.stop()
      robo.turn(-30)
      timer = StopWatch()
      while timer.time() < 2000:
            if na_linha(sensor_meio) or na_linha(sensor_esq) or na_linha(sensor_dir):
                  reset_pid()
                  return
            robo.drive(VEL_BUSCA, 30)
            wait(10)
      robo.stop()
      reset_pid()

def cruzar_gap():
      robo.drive(VEL_BUSCA, 0)
      timer = StopWatch()
      while timer.time() < 1500:
            if na_linha(sensor_meio):
                  reset_pid()
                  return True
            if na_linha(sensor_esq):
                  robo.turn(-20)
                  reset_pid()
                  return True
            if na_linha(sensor_dir):
                  robo.turn(20)
                  reset_pid()
                  return True
            robo.drive(VEL_BUSCA, 0)
            wait(10)
      robo.stop()
      return False
