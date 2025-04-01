from time import sleep, time as timer
from machine import Pin, I2C
import network
import umail
import socket
from ssd1306 import SSD1306_I2C
from hcsr04 import HCSR04
import time

# -- configuracion del keypad -- #
TECLA_ARRIBA  = const(0)
TECLA_ABAJO = const(1)

teclas = [['1', '2', '3', 'A'], ['4', '5', '6', 'B'], ['7', '8', '9', 'C'], ['*', '0', '#', 'D']]
filas = [2, 3, 4, 5]
columnas = [6, 7, 8, 9]

fila_pines = [Pin(nombre_pin, mode=Pin.OUT) for nombre_pin in filas]
columna_pines = [Pin(nombre_pin, mode=Pin.IN, pull=Pin.PULL_DOWN) for nombre_pin in columnas]

# -- init_keypad: inicializacion del keypad -- #
def init_keypad():
    for fila in range(0, 4):
        fila_pines[fila].low()

# -- scan (fila, columna): toma que tecla se esta presionado -- #
def scan(fila, columna):
    fila_pines[fila].high()
    tecla = None
    if columna_pines[columna].value() == TECLA_ABAJO:
        tecla = TECLA_ABAJO
    if columna_pines[columna].value() == TECLA_ARRIBA:
        tecla = TECLA_ARRIBA
    fila_pines[fila].low()
    return tecla

# -- tecla_cancelar_presionada(): esta es para finalizar ejecucion del programa -- #
def tecla_cancelar_presionada(oled):
    start_time = time.time()  # temporizador
    while time.time() - start_time < 1:  # max 5 seg para  que cancele
        for fila in range(4):
            for columna in range(4):
                tecla = scan(fila, columna)
                if tecla == TECLA_ABAJO and teclas[fila][columna] == "*":
                    print("Tecla '*' presionada. Cancelando...")
                    mostrar_oled(oled, "Status: Ha presionado *. Saliendo..", 1)
                    return True  
        sleep(0.1)  # mini pausa, nunca quitar
    
    # no se presiono la tecla
    #print("Tiempo agotado. Cancelando automaticamente...")
    #mostrar_oled(oled, "Tiempo agotado. Cancelando automaticamente...", 1)
    return False  

# -- obtener_fecha_hora_actual: funcion para obtener fecha y hora -- #
def obtener_fecha_hora_actual():
    current_time = timer()
    local_time = time.localtime(current_time)
    year = local_time[0]
    month = local_time[1]
    day = local_time[2]
    hour = local_time[3]
    minute = local_time[4]
    second = local_time[5]
    fecha = "{:02}/{:02}/{}".format(day, month, year)
    hora = "{:02}:{:02}:{:02}".format(hour, minute, second)
    return fecha, hora

# -- send_email(cuerpo del mensaje, distancia, fecha, hora): envio del mensaje por correo -- #
def send_email(mensaje, distance, fecha, hora):
    sender_email = "claudiaelena091@gmail.com" # correo emisor
    sender_name = "Claudia" # nombre del enviador
    sender_app_password = "nxip rybc pfqc eqju" # config del gmail
    email_subject = 'Alerta: Objeto detectado cerca' # asunto
    recipient_email = "claudiaelena091@gmail.com" # quien lo va a recibir
    try:
        smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
        smtp.login(sender_email, sender_app_password)
        smtp.to(recipient_email)
        smtp.write("From:" + sender_name + "<" + sender_email + ">\n")
        smtp.write("Subject:" + email_subject + "\n")
        smtp.write(mensaje)
        smtp.send()
        smtp.quit()
        print(f"Correo enviado. Por favor, revisar bandeja de entrada de: {recipient_email}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    return True

# -- leer_password(oled): lee la contraseña de seguridad desde el keypad con temporizador -- #
def leer_password(oled):
    password = ""
    start_time = timer()  #  timer
    mostrar_oled(oled, "Ingrese password:", 0.5)
    
    while len(password) < 4:  # pass de 4 digitos
        if timer() - start_time > 10:  # verificacion de tiempo
            cadena = "Tiempo agotado. Password incorrecta."
            print(cadena)
            mostrar_oled(oled, cadena, 2)
            return ""  # como no recibio nada, mejor retorna vacio

        tecla_presionada = False
        for fila in range(4):
            for columna in range(4):
                tecla = scan(fila, columna)
                if tecla == TECLA_ABAJO:  
                    tecla_presionada = True
                    print("Tecla presionada:", teclas[fila][columna])
                    password += teclas[fila][columna]
                    mostrar_oled(oled, f"Ingrese password: {password}", 0.2)
                    sleep(0.5)  # mini pausa para que no escriba varias veces
        if not tecla_presionada:
            sleep(0.1)  # mini pausa
    return password  # regresa contraseña ingeresada de 4 digitos

def monitoreo():
    
    # crear archivo para guardar un registro
    with open("registros.txt", "w") as file:
        file.write("identificador | fecha | hora | distancia | correo enviado\n")
    
    # instanciar sensor, pantalla oled, y led
    sensor = HCSR04(trigger_pin=27, echo_pin=26, echo_timeout_us=10000)
    oled = SSD1306_I2C(128, 64, I2C(0, scl=Pin(17), sda=Pin(16), freq=400000))
    azul = Pin(14, Pin.OUT)
    
    # var bool para continuar monitoreo
    continuar = True

    # mostrar esto para saber que ya estas en la func de monitoreo()
    cadena = "Status: CONEXION ESTABLECIDA"
    mostrar_oled(oled, cadena, 3)

    # lista para almacenar las distancias
    ultimas_distancias = []
    
    # cantidad de veces que hace el monitoreo de distancia
    # para estar seguros y no emitir falsas alarmas
    cantidad = 7
    
    # contraseña para desactivar el envio de correo
    contra = "2408"

    # bucle de monitoreo
    # la var continuar se altera si se deja presionado
    # el asterisco en el keypad
    while continuar:
        distance = round(sensor.distance_cm(), 2)
        print("Distancia:", distance, "cm")
        azul.value(1)
        
        # aqui cambia la var continuar
        if tecla_cancelar_presionada(oled):
            continuar = False
            mostrar_oled(oled, "Status: Finalizando monitoreo...", 2)
            sta = network.WLAN(network.STA_IF)
            sta.active(False)
            break
        
        # if por si da margen de error y reinicia la lista 
        if distance == -0.02:
            print("Margen de error. Sensor no tomo la medida correcta")
            cadena = "STATUS: Muestra mal tomada. Intentando de nuevo"
            mostrar_oled(oled, cadena, 0.5)
            ultimas_distancias.clear()
            
        # caso contrario de que si la tome bien
        else:
            mostrar_oled(oled, f"Distancia: {distance} cm", 0.30)
            fecha, hora = obtener_fecha_hora_actual()
            
            # condicional para verificar que la distancia anterior sea menor que la actual
            # si se cumple, elimina las distancias tomadas y reinicia la lista de
            # ultimas_distancias
            
            # se le añadio una condicional de 30 <= distance <= 60 para avisar
            # que no hay peligro, peligro existe si la distancia es menor a 30 cm
            
            if ultimas_distancias and distance > ultimas_distancias[-1] or ultimas_distancias and 50 <= distance <= 450:
                ultimas_distancias.clear()
                print("Patron de distancias reiniciado debido a aumento en la distancia.")
                mostrar_oled(oled, "STATUS: Todo tranquilo, sin peligro...", 2)
                
            
            # si no es el caso anterior, la añade 
            ultimas_distancias.append(distance)
            
            # esta condicional es para asegurar que la lista d eultimas_distancias no supere
            # el tamaño que se establecio con la var cantidad, si llega a pasar eso, elimina
            # el primer elemento
            if len(ultimas_distancias) > cantidad:
                ultimas_distancias.pop(0)
            
            # si la cantidad de elementos en ultimas_distancias coincide con la cantidad de muestras
            # entra en el bucle
            if len(ultimas_distancias) == cantidad:
                # esto es para verificar que si sea decreciente y marcarla como true
                es_decreciente = all(ultimas_distancias[i] > ultimas_distancias[i + 1] for i in range(cantidad - 1))
                
                # pausa para verificar donde se encuentra la persona
                # si esta abriendo la puerta
                
                sleep(2)  # pausa antes de tomar la nueva medida
                distance = round(sensor.distance_cm(), 2)
                print("Comparacion de distancia:", distance, "cm")
                mostrar_oled(oled, f"Distancia: {distance} cm", 0.30)
                
                # sacar diferencia de la tomada y la ultima de la lista
                diferencia_ultimas_dos = abs(distance - ultimas_distancias[-1]) <= 10
                print(f"distance: {distance} //// ultimas_distancias: {ultimas_distancias}")
                
                if distance < ultimas_distancias[-1]:
                    ultimas_distancias.clear()
                                       
                
                # entonces, si la lista es decreciente y la ult distancia esta entre 0 a 30 y
                # la diferencia de las ultimas_dos es menor o igual a 10
                if es_decreciente and 0 <= distance <= 30 and diferencia_ultimas_dos:
                    # mensaje para advertir que si entro al bucle
                    cadena = f"ALERTA! Intruso detectado. Ult. distancia: {distance}cm"
                    print(cadena)
                    mostrar_oled(oled, cadena, 2.5)
                    
                    # alerta usando el led azul
                    azul.value(1)
                    sleep(1)
                    azul.value(0)
                    sleep(1.5)
                    azul.value(1)
                    sleep(1)
                    
                    # mensaje para advertir que puede ingresar el pin de seguridad
                    cadena = "ADVERTENCIA: Tiene 10 segundos para ingresar el pin de seguridad o el correo sera enviado."
                    print(cadena)
                    mostrar_oled(oled, cadena, 2.5)
                    
                    # llamada a la funcion de leer la contraseña del keypad
                    password = leer_password(oled)
                    
                    # verificacion (contra se definio anteriormente)
                    if password == contra:
                        cadena = "Status: Password correcta, no se enviara el correo..."
                        print(cadena)
                        mostrar_oled(oled, cadena, 2.5)
                    
                    # envio de correo
                    else:
                        cadena = "Status: Password no valida. Enviando correo..."
                        print(cadena)
                        mostrar_oled(oled, cadena, 2.5)
                        mensaje = f"Alerta! Se ha detectado un intruso acercandose lentamente. Datos tomados del monitoreo.... \nDistancia: {distance}cm\nHora: {hora}\nFecha: {fecha}"
                        mostrar_oled(oled, f"Correo: {mensaje}", 3)
                        enviado = send_email(mensaje, distance, fecha, hora)
                        
                        # si resulto true
                        if enviado:
                            mostrar_oled(oled, "Status: Correo enviado", 2)
                            with open("registros.txt", "a") as file:
                                file.write(f"Alerta_{fecha}_{hora} | {fecha} | {hora} | {distance} cm | Si\n")
                        ultimas_distancias.clear()
                        print(ultimas_distancias) # verificar que si se limpio
                else:
                    ultimas_distancias.clear()  # reiniciar el patron si no se cumplen ambas condiciones
                    print("Patron de distancias reiniciado.")
                    
                    azul.value(0)
    print("Monitoreo finalizado.")


# -- mostrar_oled(instancia, mensaje str, y tiempo que permanece en la pantalla)                               
def mostrar_oled(oled, message, n):
    oled.fill(0)
    ancho_caracter = 7
    max_columna = 120
    fila = 0
    columna = 0
    palabras = message.split()
    for palabra in palabras:
        ancho_palabra = len(palabra) * ancho_caracter
        if columna + ancho_palabra > max_columna:
            fila += 16
            columna = 0
        if fila >= 50:
            oled.show()
            sleep(n)
            oled.fill(0)
            fila = 0
            columna = 0
        oled.text(palabra, columna, fila)
        columna = columna + 7
        columna += ancho_palabra + ancho_caracter
    oled.show()
    sleep(n)

# -- escanear_redes(oled): escaneo de wifis cercanas 2.4ghz -- #
def escanear_redes(oled):
    print("Escaneando redes WiFi cercanas...")
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    redes = sta.scan()
    lista_redes = []
    for red in redes:
        ssid = red[0].decode('utf-8').strip()  
        if ssid:  # verifica que no sea una cadena vacia
            lista_redes.append(ssid)
    return lista_redes

# -- conectar_a_red(oled instancia, nombre de la red, contraseña): conectar a un ap -- #
def conectar_a_red(oled, ssid, password):
    cadena = f"Conectando a {ssid}..."
    mostrar_oled(oled, cadena, 2)
    print(cadena)
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, password)
    a = 1
    while not sta.isconnected():
        print("Esperando conexion...")
        mostrar_oled(oled, f"Esperando conexion con {ssid}", 2)
        sleep(2)
        a = a + 1
        if a >= 5:
            break
    ip = sta.ifconfig()[0]
    print(f"IP: {ip}")
    if ip == "0.0.0.0":
        print("Retomando a escoger red. Conexion no aceptada. Verifique disponibilidad.")
        mostrar_oled(oled, "Conexion no establecida... Retornando", 2)
    return sta

# -- main -- #
def main():
    azul = Pin(14, Pin.OUT)
    oled = SSD1306_I2C(128, 64, I2C(0, scl=Pin(17), sda=Pin(16), freq=400000))
    
    azul.value(0)
    oled.fill(0)
    sleep(2)
    
    cadena = "SISTEMA DE SEGURIDAD DE DISTANCIA"
    mostrar_oled(oled, cadena, 4)
    print(cadena)
    
    cadena = "Status: Escaneando redes de WiFi disponibles.."
    mostrar_oled(oled, cadena, 4)
    print(cadena)
    ssid = ""
    password = ""
    
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    
    while not sta.isconnected():
        lista_redes = escanear_redes(oled)
        if lista_redes:
            cadena = "Se han encontrado redes, verifique la consola"
            mostrar_oled(oled, cadena, 3)
            print(cadena)
        else:
            cadena = "No se han encontrado redes, verifique que si exista"
            mostrar_oled(oled, cadena, 3)
            print(cadena)
        
        cadena = "Selecciona una red en consola."
        mostrar_oled(oled, cadena, 3)
        print(cadena)
        for i, red in enumerate(lista_redes):  # enlistar redes
            print(f"{i + 1}. {red}")
            
        opcion_red = int(input("Marque el numero de la red a la que desea conectar (0 para salir): "))
        if opcion_red < 1 or opcion_red > len(lista_redes):
            print("Opcion invalida. Saliendo...")
            return
        
        ssid = lista_redes[opcion_red - 1]  
        cadena = f"Red seleccionada: {ssid}. Revise consola."
        print(cadena)
        mostrar_oled(oled, cadena, 3)
        password = input("Ingrese la password de la red: ")  
        print(f"Conectando a la red: {ssid} con password: {password}")
        sta = conectar_a_red(oled, ssid, password)
        
    mostrar_oled(oled, f"Conectado a: {ssid}.. Redirigiendo..", 3)
    monitoreo()

if __name__ == "__main__":
    init_keypad()
    main()