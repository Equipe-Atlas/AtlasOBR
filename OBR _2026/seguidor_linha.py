from pybricks.hubs import PrimeHub                                  #
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor#
from pybricks.parameters import Color, Port, Direction              #   biliotecas
from pybricks.tools import wait, StopWatch                          #
from pybricks.robotics import DriveBase                             #

hub = PrimeHub(broadcast_channel=1, observe_channels=[2]) # definição do hub e dos canais

# mesmos códigos usados no hub da área de resgate
COD_ENTROU_CANTO = 100   # área de resgate avisou que parou num canto
COD_SAIDA_ESQ = 201      # achou a abertura à esquerda
COD_SAIDA_FRENTE = 202   # achou a abertura na frente
COD_SAIDA_DIR = 203      # achou a abertura à direita
COD_PRECISA_GIRAR = 209  # não achou abertura, pede pra girar um pouco e a área de resgate confere de novo
COD_LIBERA = 10000       # área de resgate terminou, devolve o controle

ultra = UltrasonicSensor(Port.C)                                        #
cordir = ColorSensor(Port.B)                                            #
cormeio = ColorSensor(Port.A)                                           # declaração de motores e sensores
coresq = ColorSensor(Port.D)                                            #
motor_esq = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)#
motor_dir = Motor(Port.E)                                               #

andar = DriveBase(motor_esq, motor_dir, 63, 133)                                                   #
andar.settings(straight_speed=100, straight_acceleration=300, turn_rate=100, turn_acceleration=300)# definição da função andar

Color.SILVER = Color(h=0, s=0, v=75)                                                #
Color.BLACK = Color(h=240 < 180, s=100 < 10, v=50 < 10)                             #
cores = (Color.GREEN, Color.SILVER, Color.BLACK, Color.WHITE, Color.NONE, Color.RED)# definição das cores que o robo pode ler
cordir.detectable_colors(cores)                                                     #  
coresq.detectable_colors(cores)                                                     #

omnitrix = StopWatch() # declaração da função para contar tempo

reflection = 36    #
vel = 150          #
kp = 4             #
ki = 0.05          #
kd = 20            #
integral = 0       # declaração das variaveis
erro_anterior = 0  #
ultimo_dist = 0    #
ultima_arfagem = 0 #
dirpreto = False   #
esqpreto = False   #
tempo = 0

def mapeia_verde(sensor):                                                     #
    dados = sensor.hsv()                                                      #
    if (160 <= dados.h <= 200) and (dados.s > 40) and (50 <= dados.v <= 100): # função ler verde
        return True                                                           #
    return False                                                              #

hub.imu.reset_heading(0) # reinicia a guinada

hub.light.on(Color.BLUE) # liga a luz azul no hub

while True: # laço de repetição infinito
    esq_e_verde = mapeia_verde(coresq)  #
    dir_e_verde = mapeia_verde(cordir)  #
    dist = ultra.distance()             #
    hub.ble.broadcast(dist)             # NOVO: manda a leitura da frente pro hub da área de resgate
    esq = coresq.color()                #
    dir = cordir.color()                #
    meio = cormeio.reflection()         # leitura de sensores
    arfagem, rolagem = hub.imu.tilt()   #
    arfagem = arfagem + 3.6             #
    hsv_esq = coresq.hsv()              #
    hsv_meio = cormeio.hsv()            #
    hsv_dir = cordir.hsv()
    mensagem = hub.ble.observe(2)
    if arfagem > 3 or arfagem < -3:
        ultima_arfagem = arfagem
        motor_esq.run(200)
        motor_dir.run(200)
        wait(200)
        arfagem, rolagem = hub.imu.tilt()
        arfagem = arfagem + 3.6   
        while arfagem > ultima_arfagem - 1 or arfagem < ultima_arfagem + 1:
            ultima_arfagem = arfagem
            motor_esq.run(200)
            motor_dir.run(200)
            wait(50)
            arfagem, rolagem = hub.imu.tilt()
            arfagem = arfagem + 3.6
            print(arfagem, "      ", ultima_arfagem)
        while arfagem > 3 or arfagem < -3:
            andar.stop()
            wait(999999)
    else:
        if mensagem == COD_ENTROU_CANTO:
            andar.stop()  #o robô fica parado enquanto espera
            ultima_mensagem_tratada = None
            while True:
                mensagem = hub.ble.observe(2)
                if mensagem == COD_LIBERA:
                    break
                elif mensagem != ultima_mensagem_tratada:
                    if mensagem == COD_SAIDA_ESQ:
                        andar.turn(-90)
                    elif mensagem == COD_SAIDA_FRENTE:
                        andar.straight(100)
                    elif mensagem == COD_SAIDA_DIR:
                        andar.turn(90)
                    elif mensagem == COD_PRECISA_GIRAR:
                        andar.turn(30)
                    ultima_mensagem_tratada = mensagem
                wait(20)
        else:
            if dist < 75:
                andar.turn(80)
                ultimo_dist = ultra.distance()
                while dist <= ultimo_dist:
                    ultimo_dist = ultra.distance()
                    motor_esq.run(-100)
                    motor_dir.run(100)
                    wait(10)
                    dist = ultra.distance()
                    if dist > 300: dist = 300
                    if ultimo_dist > 300: ultimo_dist = 300
                    if dist > (ultimo_dist + 1): dist = ultimo_dist
                    print("distância: {}, ultima: {}".format(dist, ultimo_dist))
                andar.turn(100)
                andar.straight(200)
                andar.turn(-110)
                andar.straight(400)
                andar.turn(-110)
                andar.straight(210)
                andar.turn(-115)
                motor_esq.run(-100)
                motor_dir.run(100)
                wait(2500)
                meio = cormeio.reflection()
                while meio > 80:
                    motor_esq.run(-100)
                    motor_dir.run(100)
                    meio = cormeio.reflection()
                integral = 0
                erro_anterior = 0
            else:
                if esq_e_verde and dir_e_verde or esq == Color.GREEN and dir == Color.GREEN:
                    andar.turn(-200)
                    andar.straight(50)
                elif esq_e_verde or esq == Color.GREEN:
                    if dirpreto == False or esqpreto == False:
                        while esq != Color.WHITE:
                            motor_esq.run(-50)
                            motor_dir.run(0)
                            esq = coresq.color()
                        andar.straight(15)
                        dir = cordir.color()
                        wait(100)
                        if dir == Color.GREEN:
                            andar.turn(-200)
                            andar.straight(50)
                        else:
                            andar.straight(30)
                            andar.turn(-90)
                            andar.straight(50)
                    elif esqpreto == True or dirpreto == True:
                        andar.straight(50)
                        dirpreto = False
                        esqpreto = False
                elif dir_e_verde or dir == Color.GREEN:
                    if dirpreto == False or esqpreto == False:
                        while dir != Color.WHITE:
                            motor_esq.run(0)
                            motor_dir.run(-50)
                            dir = cordir.color()
                        andar.straight(15)
                        esq = coresq.color()
                        wait(100)
                        if esq == Color.GREEN:
                            andar.turn(-200)
                            andar.straight(50)
                        else:
                            andar.straight(30)
                            andar.turn(90)
                            andar.straight(50)
                        dirpreto = False
                    elif esqpreto == True or dirpreto == True:
                        andar.straight(50)
                        dirpreto = False
                        esqpreto = False
                else:
                    if esq == Color.WHITE and meio > 50 and dir == Color.WHITE:
                        motor_esq.run(vel)
                        motor_dir.run(vel)
                        wait(200)
                    elif dir == Color.BLACK and esq == Color.BLACK:
                        motor_esq.run(vel)
                        motor_dir.run(vel)
                        dirpreto = True
                        esqpreto = True
                        wait(500)
                    else:
                        erro = reflection - meio
                        integral = integral + erro
                        if integral > 100: integral = 100
                        if integral < -100: integral = -100
                        derivada = erro - erro_anterior
                        correcao = (kp * erro) + (ki * integral) + (kd * derivada)
                        if correcao > 300: correcao = 300
                        elif correcao < -300: correcao = -300
                        if dir == Color.BLACK and dir != Color.GREEN:
                            dirpreto = True
                        elif esq == Color.BLACK and esq != Color.GREEN:
                            esqpreto = True
                        motor_esq.run(vel + correcao)
                        motor_dir.run(vel - correcao) 
                        erro_anterior = erro
                        dirpreto = False
                        esqpreto = False
    print(hsv_esq.h, hsv_esq.s, hsv_esq.v, hsv_dir.h, hsv_dir.s, hsv_dir.v, meio)
    wait(20)
