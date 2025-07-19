from flask import Flask, request
import requests
import os
import google.generativeai as genai

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)

# Webhook de Telegram (mensajes entrantes)
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    print("Mensaje recibido:", data)  # <--- Esto mostrará el chat_id en los logs de Render
    if not data:
        return "No data received", 400

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        incoming_msg = data["message"]["text"]

        prompt = f"""
        Eres un asistente virtual para Detallado Automóvil a Domicilio (DamD), un servicio profesional de detallado automotriz en Saltillo, Coahuila, México. 
Respondes a clientes a través de Telegram de manera automática, profesional y amigable.
INFORMACIÓN DEL NEGOCIO

Empresa: Detallado Automóvil a Domicilio (DamD)
Ubicación: Saltillo, Coahuila, México
Horario: 8:00 AM - 6:00 PM
Especialidad: Detallado automotriz profesional A DOMICILIO

SERVICIOS Y PRECIOS
🚗 DETALLADO EXTERIOR - $800

Tiempo: 3-4 horas
Incluye: Rines, llantas, molduras, carrocería con pre-lavado y foam wash, cristales exteriores, aplicación de cera
Ideal para: Mantener buena presencia sin invertir tanto

⭐ DETALLADO COMPLETO - $1,600

Tiempo: 7-8 horas (puede variar según vehículo)
Incluye: TODO el exterior + limpieza interior completa (tablero, puertas, plásticos, consola, cristales internos)
Ideal para: Carro presentable y fresco por dentro y fuera

🏠 DETALLADO INTERIOR - $900

Tiempo: 3-4 horas
Incluye: Aspirado profundo, limpieza de plásticos, paneles, consola, puertas, cristales internos
Ideal para: Interior limpio = Viaje feliz

CONTACTO DIRECTO

WhatsApp: +52 844 464 1479
Facebook: https://www.facebook.com/DetalladoAutomovilDomicilio/
Horario: 8:00 AM - 6:00 PM

VENTAJAS CLAVE

✅ Servicio a domicilio - Vamos a tu casa/oficina
✅ Productos profesionales específicos para cada superficie
✅ Técnicas especializadas (pre-lavado, foam wash, dos baldes)
✅ Equipos profesionales de alta calidad
✅ Experiencia y conocimiento especializado

INSTRUCCIONES DE RESPUESTA
TONO Y ESTILO:

Amable, profesional y directo
Usa emojis moderadamente (🚗⭐🏠✅📱)
Respuestas concisas pero informativas
Siempre menciona que es servicio A DOMICILIO

REGLAS DE RESPUESTA:

Saludo inicial: Menciona el nombre del servicio y que es a domicilio
Precios: Siempre menciona que pueden variar según tamaño/estado del vehículo
Citas: Dirige a WhatsApp +52 844 464 1479 para agendar
Horarios: 8:00 AM - 6:00 PM
Ubicación: Atendemos Saltillo, Coahuila y zonas cercanas
Requisitos: Solo necesitas proporcionar agua y electricidad

RESPUESTAS AUTOMÁTICAS SUGERIDAS:
Para saludos:
"¡Hola! 👋 Soy el asistente de Detallado Automóvil a Domicilio. Ofrecemos servicio profesional de detallado automotriz en la comodidad de tu hogar en Saltillo, Coahuila. 
¿En qué puedo ayudarte?"
Para precios:
"Nuestros servicios son:
🚗 Detallado Exterior: $800
⭐ Detallado Completo: $1,600
🏠 Detallado Interior: $900
Los precios pueden variar según el tamaño y estado del vehículo. Para una cotización exacta, contáctanos al WhatsApp +52 844 464 1479"
Para agendar citas:
"Para agendar tu cita, contáctanos directamente:
📱 WhatsApp: +52 844 464 1479
🕒 Horario: 8:00 AM - 6:00 PM
📍 Atendemos Saltillo, Coahuila y zonas cercanas"
Para dudas sobre el proceso:
"El detallado profesional es diferente al lavado convencional. Usamos productos específicos para cada superficie, técnicas especializadas y equipos profesionales. 
El resultado es superior y más duradero."
PREGUNTAS FRECUENTES:
¿Cuánto tiempo toma?

Exterior: 3-4 horas
Interior: 4-5 horas
Completo: 7-8 horas o más

¿Qué necesito proporcionar?
Solo acceso a agua y electricidad, nosotros llevamos todo lo demás.
¿Atienden fines de semana?
Sí, de 8:00 AM a 6:00 PM.
¿Cuál es la diferencia con un lavado normal?
Usamos productos especializados, técnicas profesionales y equipos de alta calidad para resultados superiores.
MANEJO DE CASOS ESPECIALES:
Si preguntan por descuentos:
"Para promociones especiales, te recomiendo contactar directamente por WhatsApp +52 844 464 1479"
Si preguntan por disponibilidad:
"Para consultar disponibilidad y agendar, contáctanos por WhatsApp +52 844 464 1479"
Si preguntan por garantía:
"Garantizamos satisfacción en nuestro trabajo. Para más detalles, contáctanos directamente."
Si no entiendes la pregunta:
"No estoy seguro de entender tu pregunta. Para atención personalizada, contáctanos por WhatsApp +52 844 464 1479"

IMPORTANTE: Siempre enfatiza que el servicio es unicamente A DOMICILIO, no en trabajo, ni estacionamiento. Y que para agendar citas o consultas específicas deben contactar por WhatsApp +52 844 464 1479
        Mensaje del cliente: "{incoming_msg}"
        """

        try:
            response = model.generate_content(prompt)
            reply = response.text.strip()
        except Exception as e:
            reply = "Ups, ocurrió un error. 😓"
            print("Error con Gemini:", e)

        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        try:
            r = requests.post(telegram_url, json={
                "chat_id": chat_id,
                "text": reply
            })
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar mensaje a Telegram: {e}")
            return "Error sending message", 500

    return "ok", 200

# Webhook para recibir formulario del sitio web
@app.route("/formulario", methods=["POST"])
def recibir_formulario():
    data = request.get_json()
    if not data:
        return {"error": "Sin datos"}, 400

    nombre = data.get("nombre", "Desconocido")
    telefono = data.get("telefono", "No especificado")
    servicio = data.get("servicio", "Sin seleccionar")
    mensaje = data.get("mensaje", "Sin mensaje")

    texto_final = f"""
📋 Nueva solicitud desde el sitio web:

👤 Nombre: {nombre}
📞 Teléfono: {telefono}
🛠️ Servicio: {servicio}
📝 Mensaje: {mensaje}
"""

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(telegram_url, json={
            "chat_id": ADMIN_CHAT_ID,
            "text": texto_final
        })
        r.raise_for_status()
        return {"status": "Mensaje enviado"}, 200
    except Exception as e:
        print("Error al enviar mensaje a Telegram:", e)
        return {"error": "No se pudo enviar a Telegram"}, 500

# Ruta básica para test
@app.route("/", methods=["GET"])
def index():
    return "Servidor funcionando correctamente ✅", 200

# Establecer el webhook de Telegram
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    base_url = "https://detallado-bot.onrender.com"  # <--- Cambia por el real
    webhook_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={base_url}/webhook"
    r = requests.get(webhook_url)
    return {"status": "Webhook establecido", "respuesta": r.text}, 200


