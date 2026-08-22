from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Color, Port
from pybricks.tools import wait, StopWatch

# === HUB ===
hub = PrimeHub(broadcast_channel=2, observe_channels=[1])
hub.light.on(Color.MAGENTA)

# === MOTORES E SENSORES ===
sensor_garra = ColorSensor(Port.F)   # sensor de cor na garra
ultra_esq = UltrasonicSensor(Port.B)  # ultrassônico esquerda
ultra_dir = UltrasonicSensor(Port.D)  # ultrassônico direita
garra = Motor(Port.E)                 # motor da garra (levantar/descer)
selecao = Motor(Port.C)               # palheta de seleção (vivo/morto)
descarte = Motor(Port.A)               # palheta de descarte (barreira)

# Resetar posicoes dos motores para run_target funcionar
garra.reset_angle(0)
selecao.reset_angle(0)
descarte.reset_angle(0)

# === CORES ===
Color.SILVER = Color(h=0, s=0, v=75)
Color.BLACK = Color(h=240, s=100, v=20)
Color.WHITE = Color(h=0, s=0, v=100)

# === PARAMETROS ===
dsaida = 110              # distancia para considerar abertura
PASSO = 200               # tamanho do passo em mm
TEMPO_PASSO = 2500       # tempo de espera ao andar
TEMPO_GIRO = 1200        # tempo de espera ao girar
LIMIAR_ENTRADA = 200    # se ambos ultrassonicos > isso, entrou na area

# === POSICOES DOS MOTORES (graus absolutos) ===
GARRA_CIMA = 90
GARRA_BAIXO = 0
SELECAO_NEUTRO = 0
SELECAO_VIVAS = 180
SELECAO_MORTAS = -180
DESCARTE_FECHADO = 0
DESCARTE_ABERTO = 90

# === PROTOCOLO BLE (canal 2 = Atlas -> Prometeu) ===
COD_ENTROU_CANTO = 100
COD_SAIDA_ESQ = 201
COD_SAIDA_FRENTE = 202
COD_SAIDA_DIR = 203
COD_PRECISA_GIRAR = 209
COD_LIBERA = 10000
COD_ANDA_FRENTE = 300
COD_GIRA_90 = 301

# === ESTADOS ===
ESTADO_AGUARDANDO = 0
ESTADO_VARREDURA = 1
ESTADO_CANTO = 2
ESTADO_SAIDA = 3

omnitrix = StopWatch()
estado = ESTADO_AGUARDANDO

# === FUNCOES ===

def le_dados_prometeu():
    """Le a tupla (distancia_frente, flag_resgate) do Prometeu."""
    dados = hub.ble.observe(1)
    if dados is None:
        return 0, 0
    if isinstance(dados, tuple) and len(dados) == 2:
        return dados[0], dados[1]
    return dados, 0

def le_distancia_frente():
    d, _ = le_dados_prometeu()
    return d

def verificou_entrada_area():
    """Verifica se entrou na area de resgate:
    - flag do Prometeu (faixa prata), OU
    - ambos ultrassonicos laterais abertos."""
    _, flag = le_dados_prometeu()
    if flag == 1:
        return True
    if ultra_esq.distance() > LIMIAR_ENTRADA and ultra_dir.distance() > LIMIAR_ENTRADA:
        return True
    return False

def em_canto():
    """Esta em um canto se ambos os ultrassonicos laterais < dsaida."""
    return (ultra_esq.distance() < dsaida) and (ultra_dir.distance() < dsaida)

def verifica_saida():
    """Checa os 3 ultrassonicos para encontrar saida.
    Retorna o codigo de saida correspondente ou COD_PRECISA_GIRAR."""
    d_esq = ultra_esq.distance()
    d_frente = le_distancia_frente()
    d_dir = ultra_dir.distance()

    if d_esq > dsaida:
        return COD_SAIDA_ESQ
    if d_frente > dsaida:
        return COD_SAIDA_FRENTE
    if d_dir > dsaida:
        return COD_SAIDA_DIR
    return COD_PRECISA_GIRAR

def vitima_viva(sensor):
    """Vitima viva = colorida (saturacao alta, valor alto)."""
    dados = sensor.hsv()
    return dados.s > 15 and dados.v > 60

def vitima_morta(sensor):
    """Vitima morta = escura (valor muito baixo)."""
    dados = sensor.hsv()
    return dados.v < 15

def tem_vitima(sensor):
    """Verifica se ha vitima sob o sensor da garra."""
    dados = sensor.hsv()
    # Se nao for branco/prata (fundo), pode ser vitima
    return not (dados.s < 10 and dados.v > 65)

def coleta_e_processa_vitima():
    """Pega a vitima, identifica se viva ou morta, e descarta no lado correto."""
    # 1. Levanta a garra para pegar
    garra.run_target(200, GARRA_CIMA)
    wait(300)

    # 2. Identifica o tipo de vitima
    if vitima_viva(sensor_garra):
        selecao.run_target(150, SELECAO_VIVAS)
    elif vitima_morta(sensor_garra):
        selecao.run_target(150, SELECAO_MORTAS)
    else:
        # Nao era vitima, desce a garra e volta
        garra.run_target(200, GARRA_BAIXO)
        selecao.run_target(150, SELECAO_NEUTRO)
        return

    wait(200)

    # 3. Abre a barreira de descarte
    descarte.run_target(200, DESCARTE_ABERTO)
    wait(300)

    # 4. Desce a garra (solta a vitima)
    garra.run_target(200, GARRA_BAIXO)
    wait(300)

    # 5. Fecha a barreira
    descarte.run_target(200, DESCARTE_FECHADO)
    wait(200)

    # 6. Garra volta para cima (pronta para proxima)
    garra.run_target(200, GARRA_CIMA)
    wait(200)

    # 7. Selecao volta para neutro
    selecao.run_target(150, SELECAO_NEUTRO)

def mandar_andar():
    hub.ble.broadcast(COD_ANDA_FRENTE)
    wait(TEMPO_PASSO)

def mandar_girar():
    hub.ble.broadcast(COD_GIRA_90)
    wait(TEMPO_GIRO)

# === LOOP PRINCIPAL ===
while True:

    if estado == ESTADO_AGUARDANDO:
        # Aguarda deteccao de entrada na area de resgate
        if verificou_entrada_area():
            estado = ESTADO_VARREDURA
            hub.light.on(Color.GREEN)
            wait(500)  # da tempo do Prometeu tambem entrar em modo resgate

    elif estado == ESTADO_VARREDURA:
        # Manda o Prometeu dar um passo para frente
        mandar_andar()

        # Verifica vitima com o sensor da garra
        if tem_vitima(sensor_garra):
            hub.ble.broadcast(COD_LIBERA)  # pausa o Prometeu
            wait(200)
            coleta_e_processa_vitima()

        # Verifica se chegou em um canto
        if em_canto():
            estado = ESTADO_CANTO

    elif estado == ESTADO_CANTO:
        # Sinaliza que chegou no canto
        hub.ble.broadcast(COD_ENTROU_CANTO)
        wait(200)

        # Verifica todas as 3 direcoes com os ultrassonicos
        resultado = verifica_saida()

        if resultado in (COD_SAIDA_ESQ, COD_SAIDA_FRENTE, COD_SAIDA_DIR):
            # Encontrou a saida
            hub.ble.broadcast(resultado)
            wait(300)
            hub.ble.broadcast(COD_LIBERA)
            estado = ESTADO_SAIDA
        else:
            # Nao tem saida, gira 90 e continua a varredura
            hub.ble.broadcast(COD_LIBERA)
            wait(100)
            mandar_girar()
            estado = ESTADO_VARREDURA

    elif estado == ESTADO_SAIDA:
        # O Prometeu ja recebeu o codigo de saida e vai navegar para fora
        # Atlas aguarda e volta ao estado de aguardo
        hub.light.on(Color.MAGENTA)
        wait(5000)
        estado = ESTADO_AGUARDANDO

    wait(20)