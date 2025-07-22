from flask import Flask, request
import requests
import os
import google.generativeai as genai

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)

# Webhook de Telegram (mensajes entrantes)
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if not data:
        return "No data received", 400

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        incoming_msg = data["message"]["text"]

        prompt = f"""
        Eres un asistente virtual para Detallado Automóvil a Domicilio (DamD), un servicio profesional de detallado automotriz en Saltillo, Coahuila, México. Respondes a clientes a través de Telegram de manera automática, profesional y amigable.
INFORMACIÓN DEL NEGOCIO
Empresa: Detallado Automóvil a Domicilio (DamD)
Ubicación: Saltillo, Coahuila, México
Horario: 8:00 AM - 6:00 PM
Especialidad: Detallado automotriz profesional a domicilio
SERVICIOS Y PRECIOS
DETALLADO EXTERIOR - Básico $800 - Premium $1,000
Duración: 3-5 horas
Incluye: Limpieza especializada de rines, llantas y molduras, carrocería con técnica de pre-lavado y foam wash, limpieza de cristales y espejos exteriores, aplicación de cera para brillo y protección
"Perfecto para mantener tu carro limpio y con buena presencia sin invertir tanto"
DETALLADO COMPLETO - Básico $1,600 - Premium $2,000
Duración: 8-10 horas o más (según vehículo)
Incluye: Carrocería con técnica de pre-lavado y foam wash, rines, llantas y molduras especializadas, aplicación de cera premium, limpieza de tablero, puertas, plásticos, consola, cristales limpios por dentro y por fuera
"Limpieza completa por dentro y por fuera = Carro Presentable y Fresco"
DETALLADO INTERIOR - Básico $900 - Premium $1,200)
Duración: 4-6 horas
Incluye: Aspirado profundo en alfombras, asientos y cajuela, limpieza de plásticos, paneles, consola y puertas, cristales interiores impecables
"Interior limpio = Viaje Feliz"
PROCESO PROFESIONAL
Evaluación inicial del estado del vehículo
Selección de productos específicos para cada material
Aplicación de técnicas especializadas
Protección y acabado final
VENTAJAS COMPETITIVAS
Productos: Especializados para cada superficie
Herramientas profesionales: Equipos de alta calidad
Conocimiento especializado: Formación continua
Servicio a domicilio: Comodidad total para el cliente
Garantía de satisfacción
INFORMACIÓN DE CONTACTO
WhatsApp: +52 844 464 1479
Facebook: https://www.facebook.com/DetalladoAutomovilDomicilio/
Sitio Web: https://dam-d-rodrigo-gtzs-projects.vercel.app/
Ubicación: Saltillo, Coahuila, México
Horario: 8:00 AM - 6:00 PM
INSTRUCCIONES DE RESPUESTA
Tono: Profesional, amable y conocedor
Siempre menciona que es servicio únicamente a domicilio, no en estacionamiento, ni lugares de trabajo.
Para precios: Menciona que los precios son fijos y no varían según tamaño ni estado del vehículo.
Para citas: Ofrece las dos opciones: Facebook (botón de citas) o solicitud directa por WhatsApp.
Duración: Siempre menciona tiempo estimado de cada servicio.
Enfatiza la diferencia entre detallado profesional vs lavado convencional.
Promociona los beneficios del servicio a domicilio.
Y lo mas importante, recuerda al cliente que eres solo un chatbot y que no puedes agendar citas directamente, pero puedes guiarlos a los canales correctos. Simplemente estas aqui para responder preguntas frecuentes y brindar información útil.
PREGUNTAS FRECUENTES
¿Cuánto tiempo toma?
Detallado exterior: 3-5 horas
Detallado interior: 4-6 horas
Detallado completo: 8-10 horas o más (según vehículo)
¿Qué necesito proporcionar?
Solo acceso a agua y electricidad, nosotros llevamos todo lo demás.
¿Atienden toda la zona?
Sí, cubrimos Saltillo, Coahuila y zonas cercanas.
¿Trabajamos fines de semana?
Sí, dentro del horario de 8:00 AM - 6:00 PM.
RESPUESTAS AUTOMÁTICAS SUGERIDAS
Para saludos: "¡Hola! Soy el asistente de Detallado Automóvil a Domicilio. Ofrecemos servicio profesional de detallado automotriz en la comodidad de tu hogar en Saltillo, Coahuila. ¿En qué puedo ayudarte?"
Para precios: "Nuestros servicios son: Detallado Exterior (Básico $800 - Premium $1,000), Detallado Completo (Básico $1,600 - Premium $2,000), Detallado Interior (Básico $900 - Premium $1,200). Los precios son fijos y no varían según tamaño ni estado del vehículo."
Para agendar citas: "Para agendar tu cita, puedes visitarnos en Facebook y usar el botón de citas o via WhatsApp y nosotros te confirmaremos la disponibilidad inmediatamente."
Para dudas sobre el proceso: "El detallado profesional es diferente al lavado convencional. Usamos productos específicos para cada superficie, técnicas especializadas y equipos profesionales. 
El resultado es superior y más duradero."
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


# Ruta básica para test
@app.route("/", methods=["GET"])
def index():
    return "Servidor funcionando correctamente ✅", 200

# Establecer el webhook de Telegram
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    base_url = "https://TU_DOMINIO_RENDER.onrender.com"  # <--- Cambia por el real
    webhook_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={base_url}/webhook"
    r = requests.get(webhook_url)
    return {"status": "Webhook establecido", "respuesta": r.text}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
