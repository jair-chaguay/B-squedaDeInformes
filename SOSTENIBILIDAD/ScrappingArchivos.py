import os
import pdfplumber
import webbrowser
from tkinter import *
from tkinter import filedialog, messagebox
from googlesearch import search


from googlesearch import search
import webbrowser

def buscar_informe_web(empresa, anio):
    query = f"{empresa} informe anual {anio}"
    texto_salida.insert(END, f"🔎 Buscando: {query}\n\n")
    
    try:
        links = list(search(query, num_results=5))
        if links:
            for i, link in enumerate(links, 1):
                texto_salida.insert(END, f"{i}. {link}\n")
                # Hacer el link clicable
                texto_salida.tag_add(f"link{i}", f"{float(i+2)}.3", f"{float(i+2)}.{3+len(link)}")
                texto_salida.tag_config(f"link{i}", foreground="blue", underline=True)
                texto_salida.tag_bind(f"link{i}", "<Button-1>", lambda e, url=link: webbrowser.open(url))
        else:
            texto_salida.insert(END, "❌ No se encontraron resultados.\n")
    except Exception as e:
        texto_salida.insert(END, f"⚠️ Error al buscar: {e}\n")


def revisar_pdf(ruta, palabras):
    try:
        import re
        coincidencias = []
        with pdfplumber.open(ruta) as pdf:
            for i, page in enumerate(pdf.pages):
                texto = page.extract_text()
                if texto:
                    # Detectar punto, interrogación o exclamación seguido de salto de línea como fin de párrafo
                    texto_para = re.sub(r'([.!?])\s*\n', r'\1<PARA>', texto)
                    parrafos = [p.strip().replace('<PARA>', '') for p in texto_para.split('<PARA>') if p.strip()]
                    for parrafo in parrafos:
                        for palabra in palabras:
                            if palabra.lower() in parrafo.lower():
                                coincidencias.append((i + 1, parrafo))
                                break
        return coincidencias
    except Exception as e:
        print(f"Error leyendo PDF {ruta}: {e}")
        return []

def buscar_informes_locales(directorio, palabras):
    resultados = {}
    for archivo in os.listdir(directorio):
        ruta = os.path.join(directorio, archivo)
        if archivo.lower().endswith(".pdf"):
            coincidencias = revisar_pdf(ruta, palabras)
            if coincidencias:
                resultados[archivo] = coincidencias
    return resultados

# --------- INTERFAZ ---------
def seleccionar_carpeta():
    carpeta = filedialog.askdirectory()
    if not carpeta:
        return

    palabras_input = entrada_palabras.get()
    if not palabras_input.strip():
        messagebox.showerror("Error", "Por favor ingresa al menos una palabra clave.")
        return

    palabras = [p.strip().lower() for p in palabras_input.split(',') if p.strip()]
    if not palabras:
        messagebox.showerror("Error", "Lista de palabras clave vacía.")
        return

    texto_salida.delete(1.0, END)
    resultados = buscar_informes_locales(carpeta, palabras)
    if resultados:
        for archivo, coincidencias in resultados.items():
            texto_salida.insert(END, f"✅ {archivo}:\n")
            for pagina, fragmento in coincidencias:
                texto_salida.insert(END, f"   Página {pagina}: {fragmento}\n")
    else:
        texto_salida.insert(END, "❌ No se encontró información relevante en los documentos PDF.")

# --------- UI PRINCIPAL ---------
root = Tk()
root.title("Analizador de Reportes de Sostenibilidad")
root.geometry("750x550")
root.resizable(False, False)

Label(root, text="Ingrese las palabras clave separadas por comas:", font=("Arial", 11)).pack(pady=10)

entrada_palabras = Entry(root, font=("Arial", 11), width=80)
entrada_palabras.insert(0, "huella de carbono, sostenibilidad")
entrada_palabras.pack(pady=5)

Label(root, text="Seleccione el modo de búsqueda:", font=("Arial", 12)).pack(pady=10)

frame_botones = Frame(root)
frame_botones.pack()

boton_local = Button(frame_botones, text="Buscar en Archivos PDF Locales", command=seleccionar_carpeta, bg="#a9dfbf", width=30)
boton_local.pack(side=LEFT, padx=10)

texto_salida = Text(root, wrap=WORD, font=("Courier", 10), width=90, height=20)
texto_salida.pack(pady=20)

# Campos para búsqueda web
frame_web = Frame(root)
frame_web.pack(pady=10)

Label(frame_web, text="Empresa:", font=("Arial", 11)).grid(row=0, column=0, padx=5)
entrada_empresa = Entry(frame_web, font=("Arial", 11), width=30)
entrada_empresa.grid(row=0, column=1, padx=5)

Label(frame_web, text="Año:", font=("Arial", 11)).grid(row=0, column=2, padx=5)
entrada_anio = Entry(frame_web, font=("Arial", 11), width=10)
entrada_anio.grid(row=0, column=3, padx=5)

def ejecutar_busqueda_web():
    nombre_empresa = entrada_empresa.get().strip()
    anio = entrada_anio.get().strip()
    if not nombre_empresa or not anio:
        messagebox.showerror("Error", "Por favor ingrese el nombre de la empresa y el año.")
        return
    texto_salida.delete(1.0, END)
    buscar_informe_web(nombre_empresa, anio)

# Botón de búsqueda web
boton_web = Button(frame_botones, text="Buscar Informe en la Web", command=ejecutar_busqueda_web, bg="#f9e79f", width=30)
boton_web.pack(side=LEFT, padx=10)

root.mainloop()