import os
import discord
import requests
import asyncio
from datetime import datetime
from flask import Flask
from threading import Thread
from waitress import serve  # Importamos Waitress

# Configuración del servidor Flask para mantener el Repl activo
app = Flask('')

@app.route('/')
def home():
    return "Bot está activo"

def run():
    # Usamos waitress.serve para ejecutar la aplicación en producción.
    serve(app, host='0.0.0.0', port=8080)

# Inicia el servidor Flask en un hilo separado con Waitress
Thread(target=run).start()

# Configuración del cliente de Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Lista de textos de error que indican que el Space está inactivo o requiere reinicio
error_texts = [
    "Error", "Runtime Error", "Build Error", 
    "Restart Space", "This Space is sleeping due to inactivity"
]

# Función para obtener la fecha y hora actual
def get_current_time():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# Función para verificar el estado del Space
async def check_space_status():
    channel_id = int(os.getenv("CHANNEL_ID"))
    role_id = int(os.getenv("ROLE_ID"))
    space_url = os.getenv("SPACE_URL")
    channel = client.get_channel(channel_id)

    # Verificación del canal antes de iniciar el bucle
    if channel is None:
        print("Error: No se pudo obtener el canal. Verifica el ID del canal en las variables de entorno.")
        return  # Salir de la función si el canal no se encontró

    while True:
        try:
            # Hacemos una solicitud a la URL del Space
            response = requests.get(space_url)
            current_time = get_current_time()  # Obtener la hora y fecha actual

            hyperlink = f"[Acceder al Space]({space_url})"

            if response.status_code == 200:
                page_content = response.text

                # Verificamos si alguno de los textos de error está en el contenido de la página
                if any(error_text in page_content for error_text in error_texts):
                    print(f"El Space está inactivo ({current_time}).")
                    await channel.send(f"⚠️ <@&{role_id}> El Space está inactivo ({current_time}). Favor de verificar. {hyperlink}")
                else:
                    print(f"El Space está activo ({current_time}).")
                    await channel.send(f"✅ El Space está activo ({current_time}).")
            else:
                # Código de estado diferente a 200 significa que el Space tiene problemas
                print(f"El Space está inactivo (código de estado distinto de 200) ({current_time}).")
                await channel.send(f"⚠️ <@&{role_id}> El Space está inactivo ({current_time}). Favor de verificar.{hyperlink}")
        except requests.exceptions.RequestException as e:
            current_time = get_current_time()  # Obtener la hora y fecha actual en caso de error
            print(f"Error al acceder al Space: {e} ({current_time})")
            await channel.send(f"⚠️ <@&{role_id}> El Space está inactivo ({current_time}). Favor de verificar.")

        # Espera de 5 minutos antes de hacer la siguiente verificación
        await asyncio.sleep(300)

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    # Inicia la tarea de verificación del Space
    client.loop.create_task(check_space_status())

# Inicia el bot de Discord
client.run(os.getenv("DISCORD_BOT_TOKEN"))
