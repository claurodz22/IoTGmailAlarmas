# IoT Gmail Alarmas

Este proyecto fue desarrollado para la materia de Proyectos Digitales Avanzados (9no semestre UDO Ing. en Computación). Consiste en un sistema de alarmas basado en IoT que utiliza una Raspberry Pi Pico W y diversos componentes para detectar intrusiones y enviar notificaciones a través de Gmail.

## Descripción del Proyecto

El sistema está diseñado para monitorear un área específica y detectar movimientos o intrusiones utilizando un sensor ultrasónico HCSR-04. Al detectar una anomalía, el sistema activa una alarma visual mediante un LED azul y envía una notificación por correo electrónico al usuario. Además, incorpora un teclado Keypad para la interacción y configuración del sistema.

Se ha elaborado un informe detallado que describe el proceso de detección de alarmas y los métodos implementados para evitar falsas alarmas. El código fuente está estructurado en funciones con comentarios explicativos para facilitar su comprensión y mantenimiento.

## Componentes Utilizados

- **Raspberry Pi Pico W**: Microcontrolador principal que gestiona la lógica del sistema y la conectividad Wi-Fi.
- **Pantalla OLED SSD1306**: Muestra información relevante sobre el estado del sistema.
- **Sensor ultrasónico HCSR-04**: Detecta movimientos o intrusiones en el área monitoreada.
- **LED azul**: Indica visualmente la activación de la alarma.
- **Teclado Keypad**: Permite la interacción y configuración del sistema por parte del usuario.

## Requisitos

- **Hardware**:
  - Raspberry Pi Pico W
  - Pantalla OLED SSD1306
  - Sensor ultrasónico HCSR-04
  - LED azul
  - Teclado Keypad
  - Cables y conexiones necesarias

- **Software**:
  - MicroPython instalado en la Raspberry Pi Pico W
  - Bibliotecas específicas detalladas en el código fuente

## Instalación y Configuración

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/claurodz22/IoTGmailAlarmas.git
