import os
import time
import json
import glob
import paho.mqtt.client as paho
from PIL import Image
import streamlit as st
from bokeh.models import Button, CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# Funciones de MQTT
def on_publish(client, userdata, result):
    """Callback para la publicación."""
    print("El dato ha sido publicado.\n")
    pass

def on_message(client, userdata, message):
    """Callback para la recepción de mensajes."""
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# Configuración del cliente MQTT
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("litjoev2")
client1.on_message = on_message

# Título y subtítulo de la aplicación
st.title("🌐 Interfaces Multimodales")
st.subheader("🎤 CONTROL POR VOZ")

# Cargar y mostrar la imagen
image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

# Instrucciones para el usuario
st.write("🔊 Toca el botón y habla:")

# Botón para iniciar el reconocimiento de voz
stt_button = Button(label=" Inicio ", width=200)

# Código JavaScript para reconocimiento de voz
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# Manejo de eventos de Streamlit
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result:
    if "GET_TEXT" in result:
        # Mostrar el texto reconocido
        recognized_text = result.get("GET_TEXT").strip()
        st.write(f"Texto Reconocido: **{recognized_text}**")
        
        # Publicar el mensaje en el broker MQTT
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": recognized_text})
        client1.publish("conectate", message)

# Crear directorio temporal si no existe
try:
    os.mkdir("temp")
except FileExistsError:
    pass
