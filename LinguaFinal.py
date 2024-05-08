#PopUP Implementado

import tkinter as tk
import speech_recognition as sr
import serial
import time 

import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
arduino = serial.Serial(port='COM7', baudrate=9600, timeout=.1) 

riesgos = ["pistola", "disparo", "sangre",
        "incendio", "arma", "bala", "accidente",
        "heridos", "volteado", "choque", "fuego", "secuestraron",
        "muerto", "muerta", "cadaver"]

#Bloque de reconocimiento
recognizer = sr.Recognizer()
audio_file = "AudioProcesado2.wav" 

with sr.AudioFile(audio_file) as source:
    audio_data = recognizer.record(source)

try:
    recognized_text = recognizer.recognize_google(audio_data, language="es-ES")  # Puedes usar otros motores como 'recognize_bing' o 'recognize_ibm' aquí
    recognized_text = recognized_text.lower()
    print("Texto reconocido:", recognized_text)

    # Guarda el texto reconocido en un archivo de texto
    output_text_file = "texto_transcrito.txt"  # Nombre del archivo de texto de salida

    with open(output_text_file, "w") as text_file:
        text_file.write(recognized_text)

    print(f"El texto ha sido guardado en {output_text_file}")

except sr.UnknownValueError:
    print("No se pudo reconocer el audio")
except sr.RequestError as e:
    print("Error en la solicitud al servicio de reconocimiento de voz; {0}".format(e))

def print_text():
    t = entry.get()
    entry.delete(0, len(t))
    riesgos.append(t)
    resaltarRiesgo(t)
    busqueda()
    print(riesgos)

def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    #data = arduino.readline() 
    #return data 

def detecteDeRiesgos(llamada):
    llamadaSep = llamada.split()
    encontradas = [palabra for palabra in riesgos if palabra in llamada]
    return encontradas


def resaltarRiesgo(riesgo):
    start_index = "1.0"
    while True:
        start_index = text_widget.search(riesgo, start_index, stopindex="end")
        if not start_index:
            break
        end_index = f"{start_index}+{len(riesgo)}c"
        text_widget.tag_add("colored", start_index, end_index)
        text_widget.tag_config("colored", foreground="red")
        start_index = end_index

def open_popup(intencion):
    popup = tk.Toplevel()
    popup.title("Recomendación generada")

    label = tk.Label(popup, text=intencion, font = 12)
    label.grid(row=0, column=0, columnspan=2, pady=10)

    popup.geometry("222x160")  

    button_font = ("Arial", 12)

    button_width = 10
    button_height = 4

    if("Policía" in intencion):    
        mensaje = "Av. Corregidora 236 Robo Armado"
    elif("Ambulancia" in intencion):
        mensaje = "Av. Corregidora 159 Homicidio"
    elif("Bomberos" in intencion):
        mensaje = "Av. Corregidora 302 Incendio"

    yes_button = tk.Button(popup, text="Sí", command=lambda: write_read(mensaje), width=button_width, height=button_height, font=button_font)
    yes_button.grid(row=1, column=0, padx=5, pady=5)

    close_button = tk.Button(popup, text="No", command=popup.destroy, width=button_width, height=button_height, font=button_font)
    close_button.grid(row=1, column=1, padx=5, pady=5)

    popup.mainloop()

def busqueda():
    palabras_a_buscar_1 = ["disparo", "pistola"]
    palabras_a_buscar_2 = ["sangre"]
    palabras_a_buscar_3 = ["fuego", "incendio"]

    encontradas_1 = [palabra for palabra in palabras_a_buscar_1 if palabra in recognized_text]
    encontradas_2 = [palabra for palabra in palabras_a_buscar_2 if palabra in recognized_text]
    encontradas_3 = [palabra for palabra in palabras_a_buscar_3 if palabra in recognized_text]

    if encontradas_1:
        print(f'Las palabras "{encontradas_1}" se encuentran en el texto. Llamar a Policía')
        open_popup("¿Llamar a Policía?")
    elif encontradas_2:
        print(f'Las palabras "{encontradas_2}" se encuentran en el texto. Llamar a Ambulancia')
        open_popup("¿Llamar a Ambulancia?")
    elif encontradas_3:
        print(f'Las palabras "{encontradas_3}" se encuentran en el texto. Llamar Bomberos')
        open_popup("¿Llamar a Bomberos?")
    else:
        print('No hay coincidencia')

analyzer = SentimentIntensityAnalyzer()
sentimientos = analyzer.polarity_scores(recognized_text)

window = tk.Tk()
window.geometry("1100x200")  # Establece el tamaño de la ventana

# Crea un marco para la parte izquierda
left_frame = tk.Frame(window)
left_frame.pack(side="left", fill="both", expand=True)

# Crea un marco para la parte derecha
right_frame = tk.Frame(window)
right_frame.pack(side="right", fill="both", expand=True)

Nombre = tk.Label(right_frame, text="Lingua Rescue", font=("Arial", 20))
Nombre.pack()

entry = tk.Entry(right_frame, fg="black", bg="white", width=20)
entry.pack()

button = tk.Button(
    right_frame,
    text="Añadir palabra",
    width=13,
    height=2,
    bg="gray",
    fg="white",
    command=print_text
)
button.pack()

pos = "Positividad {:.1f}%".format(sentimientos['pos'] * 100)
Positividad = tk.Label(right_frame, text=pos, font=("Arial", 12))
Positividad.pack()

neg = "Negatividad {:.1f}%".format(sentimientos['neg'] * 100)
Negatividad = tk.Label(right_frame, text=neg, font=("Arial", 12))
Negatividad.pack()

neu = "Neutralidad {:.1f}%".format(sentimientos['neu'] * 100)
Neutralidad = tk.Label(right_frame, text=neu, font=("Arial", 12))
Neutralidad.pack()

enc = detecteDeRiesgos(recognized_text)

text_widget = tk.Text(left_frame, wrap=tk.WORD, font=("Arial", 15))  #  tk.WORD permite ajustar el texto por palabras
text_widget.insert("1.0", recognized_text)
for r in enc:
    resaltarRiesgo(r)

text_widget.pack(fill="both", expand=True)


busqueda()
window.mainloop()
