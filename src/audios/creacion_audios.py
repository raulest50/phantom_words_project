from gtts import gTTS
frases = ["¿Lo ves, Ana?", "No ve nada", "Mamá llama", "Una vez más", "Sabe mal", "No lo es"]
for f in frases:
    tts = gTTS(f, lang="es")
    nombre = f.replace(" ", "_").replace("¿","").replace("?","") + ".mp3"
    tts.save(nombre)
