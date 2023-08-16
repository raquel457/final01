import os
from winsound import PlaySound
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request
import json
from transcriber import Transcriber
from llm import LLM
from weather import Weather
from tts import TTS
from pc_command import PcCommand
import elevenlabs

#Cargar llaves del archivo .env
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("recorder.html")

@app.route("/audio", methods=["POST"])
def audio():
    audio = request.files.get("audio")
    audio.save("audio.mp3")
    audio_file = open("auido.mp3", "rb")
    transcribed = openai.Audio.transcribe("whisper-1", audio_file)
    text = Transcriber().transcribe(audio)
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content":"Eres un asistente divertido"}
        ]
    )

    result = ""
    for choice in response.choices:
        result += choice.message.content

    #tts = gTTS(result, lang='es', tld='com.mx')
    #tts.save("response.mp3")
    #PlaySound("response.mp3")
    
    from elevenlabs import generate, play
 
    audio = generate(
    voice= "Maya",
    model='eleven_multilingual_v1'
    )
 
    play(audio)


    llm = LLM()
    function_name, args, message = llm.process_functions(text)
    if function_name is not None:
             #se desea llamar a una función
        if function_name == "get_weather":
            #Llamar a la función del clima
            function_response = Weather().get(args["ubicacion"])
            function_response = json.dumps(function_response)
            print(f"Respuesta de la funcion: {function_response}")
            
            final_response = llm.process_response(text, message, function_name, function_response)
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}

            #enviar un correo
        elif function_name == "send_email":
            final_response = "de acuerdo, ahora escribo el correo"
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
            #abrir google chrome
        elif function_name == "open_chrome":
            PcCommand().open_chrome(args["website"])
            final_response = "Listo, ya abrí chrome en el sitio " + args["website"]
            tts_file = TTS().process(final_response)
            return {"result": "ok", "text": final_response, "file": tts_file}
        
    else:
        final_response = "No tengo idea de lo que estás hablando"
        tts_file = TTS().process(final_response)
        return {"result": "ok", "text": final_response, "file": tts_file}