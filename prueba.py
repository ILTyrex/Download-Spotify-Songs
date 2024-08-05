import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
from tkinter import messagebox, Canvas, Frame, Scrollbar
import yt_dlp 

# Especificar la ubicación de ffmpeg
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg-7.0.1-essentials_build\bin"

# Configurar tus credenciales de Spotify
client_id = ' '
client_secret = ' '

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# Variables globales
id_spotify = None
tipo = None
plataforma = None
tracks = []

# Función para obtener el ID de la playlist o canción desde el enlace
def obtener_id_desde_enlace(enlace):
    spotify_pattern = r"(playlist|track)/([a-zA-Z0-9]+)"
    youtube_pattern = r"(?:v=|list=)([a-zA-Z0-9_-]+)"
    
    if "spotify" in enlace:
        match = re.search(spotify_pattern, enlace)
        if match:
            return match.group(2), match.group(1), "spotify"
    elif "youtube" in enlace or "youtu.be" in enlace:
        match = re.search(youtube_pattern, enlace)
        if match:
            return match.group(1), "video" if "v=" in enlace else "playlist", "youtube"
    return None, None, None

# Función para obtener todas las pistas de la lista de reproducción de Spotify
def obtener_todas_las_pistas_spotify(playlist_id):
    tracks = []
    try:
        results = sp.playlist_tracks(playlist_id, offset=0)
        tracks.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
    except Exception as e:
        print(f"Error al obtener las pistas de la lista de reproducción de Spotify: {e}")
        raise
    return tracks

# Función para limpiar la lista de canciones en la GUI
def limpiar_lista_canciones():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

# Función para manejar el enlace ingresado
def manejar_enlace(enlace):
    global id_spotify, tipo, plataforma, tracks  # Variables globales para acceder desde otras funciones
    id_spotify, tipo, plataforma = obtener_id_desde_enlace(enlace)

    # Limpiar la lista de canciones antes de mostrar nuevas, solo si es una canción individual
    if tipo == 'track':
        limpiar_lista_canciones()

    if plataforma == 'spotify':
        try:
            if tipo == 'playlist':
                tracks = obtener_todas_las_pistas_spotify(id_spotify)
                mostrar_canciones()

                btn_descargar_seleccionadas.config(state=tk.NORMAL)
                btn_descargar_todas.config(state=tk.NORMAL)

            elif tipo == 'track':
                track = sp.track(id_spotify)
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                print(f"Canción: {track_name} - {artist_name}")

                # Verificar si la canción ya está descargada 
                if not cancion_descargada(track_name):
                    descargar_cancion_especifica(track_name, artist_name)
                else:
                    messagebox.showinfo("Ya descargada", f"La canción {track_name} ya está descargada.")

                # Mostrar previsualización de la canción individual
                limpiar_lista_canciones()
                mostrar_cancion_individual(track_name, artist_name)

            else:
                print("Enlace no válido. Por favor, ingresa un enlace de playlist o canción de Spotify válido.")
                messagebox.showerror("Error", "Enlace no válido. Por favor, ingresa un enlace de playlist o canción de Spotify válido.")

        except Exception as e:
            print(f"Error al procesar el enlace de Spotify: {e}")
            messagebox.showerror("Error", f"Error al procesar el enlace de Spotify: {e}")

    elif plataforma == 'youtube':
        if tipo == "playlist":
            descargar_playlist_youtube(id_spotify)
        else:
            descargar_cancion_youtube(id_spotify)

    else:
        print("Enlace no válido. Por favor, ingresa un enlace de playlist o canción de Spotify o YouTube válido.")
        messagebox.showerror("Error", "Enlace no válido. Por favor, ingresa un enlace de playlist o canción de Spotify o YouTube válido.")

# Función para mostrar una canción individual en la GUI
def mostrar_cancion_individual(track_name, artist_name):
    check_var = tk.BooleanVar()
    check_btn = tk.Checkbutton(scrollable_frame, text=f"{track_name} - {artist_name}", variable=check_var)
    check_btn.grid(row=0, column=0, sticky="w")
    check_btn.var = check_var  

    scrollbar.config(command=canvas.yview)
    canvas.configure(scrollregion=canvas.bbox("all"))
# Función para descargar una playlist de YouTube
def descargar_playlist_youtube(playlist_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'socket_timeout': 60,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/playlist?list={playlist_id}"])
    except Exception as e:
        print(f"Error al descargar la playlist de YouTube: {e}")
        with open('errores.txt', 'a', encoding='utf-8') as f:
            f.write(f"Playlist de YouTube - {playlist_id}: {e}\n")

# Función para descargar una canción de YouTube
def descargar_cancion_youtube(video_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'socket_timeout': 60,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
    except Exception as e:
        print(f"Error al descargar la canción de YouTube: {e}")
        with open('errores.txt', 'a', encoding='utf-8') as f:
            f.write(f"Canción de YouTube - {video_id}: {e}\n")

# Función para descargar las canciones seleccionadas en la GUI
def descargar_seleccionadas():
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, tk.Checkbutton):
            if widget.var.get():
                try:
                    idx = int(widget.cget("text").split('.')[0]) - 1
                    if 0 <= idx < len(tracks):
                        track = tracks[idx]['track']
                        track_name = track['name']
                        artist_name = track['artists'][0]['name']

                        if not cancion_descargada(track_name):
                            descargar_cancion_especifica(track_name, artist_name)
                except ValueError:
                    print(f"Error: no se pudo obtener el índice de la canción desde el texto del Checkbutton: {widget.cget('text')}")

    messagebox.showinfo("Completado", "Descarga de canciones seleccionadas completada.")

# Función para seleccionar todas las canciones en la GUI
def seleccionar_todas():
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, tk.Checkbutton):
            widget.var.set(True)

# Función para deseleccionar todas las canciones en la GUI
def deseleccionar_todas():
    for widget in scrollable_frame.winfo_children():
        if isinstance(widget, tk.Checkbutton):
            widget.var.set(False)

# Función para verificar si una canción ya está descargada
def cancion_descargada(track_name):
    return os.path.isfile(f"{track_name}.mp3")

# Función para descargar una canción específica de Spotify
def descargar_cancion_especifica(track_name, artist_name):
    search_query = f"{track_name} {artist_name}"

    # Verificar si la canción ya está descargada
    if cancion_descargada(track_name):
        print(f"{track_name} ya está descargada.")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'socket_timeout': 60,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            query = ydl.extract_info(f"ytsearch1:{search_query}", download=False)['entries'][0]
            if query:
                ydl.download([query['webpage_url']])
                print(f"Canción descargada: {track_name} - {artist_name}")
    except Exception as e:
        print(f"Error al descargar {track_name} de {artist_name}: {e}")
        with open('errores.txt', 'a', encoding='utf-8') as f:
            f.write(f"{track_name} - {artist_name}: {e}\n")

# Función para mostrar las canciones en la GUI
def mostrar_canciones():
    for i, track in enumerate(tracks):
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        
        check_var = tk.BooleanVar()
        check_btn = tk.Checkbutton(scrollable_frame, text=f"{i+1}. {track_name} - {artist_name}", variable=check_var, font=("Helvetica", 10))
        check_btn.grid(row=i, column=0, sticky="w", padx=10, pady=5)
        check_btn.var = check_var  # Asociar la variable BooleanVar al Checkbutton

    scrollbar.config(command=canvas.yview)
    canvas.configure(scrollregion=canvas.bbox("all"))

# interfaz gráfica
root = tk.Tk()
root.title("Descargar Canciones")

frame = tk.Frame(root)
frame.pack(pady=20)

label_enlace = tk.Label(frame, text="Ingresa el enlace de la playlist o canción de Spotify o YouTube:", font=("Helvetica", 12))
label_enlace.grid(row=0, column=0, padx=10, pady=10)

entry_enlace = tk.Entry(frame, width=50, font=("Helvetica", 12))
entry_enlace.grid(row=0, column=1, padx=10, pady=10)

btn_descargar = tk.Button(frame, text="Descargar", font=("Helvetica", 12), command=lambda: manejar_enlace(entry_enlace.get()))
btn_descargar.grid(row=0, column=2, padx=10, pady=10)

lista_canciones_frame = tk.Frame(root)
lista_canciones_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(lista_canciones_frame)
scrollbar = tk.Scrollbar(lista_canciones_frame, orient=tk.VERTICAL)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill=tk.BOTH, expand=True)

scrollable_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

btn_descargar_todas = tk.Button(root, text="Descargar Todas", state=tk.DISABLED, font=("Helvetica", 12), command=descargar_seleccionadas)
btn_descargar_todas.pack(pady=10)

btn_descargar_seleccionadas = tk.Button(root, text="Descargar Seleccionadas", state=tk.DISABLED, font=("Helvetica", 12), command=descargar_seleccionadas)
btn_descargar_seleccionadas.pack(pady=10)

btn_seleccionar_todas = tk.Button(root, text="Seleccionar Todas", font=("Helvetica", 12), command=seleccionar_todas)
btn_seleccionar_todas.pack(pady=10)

btn_deseleccionar_todas = tk.Button(root, text="Deseleccionar Todas", font=("Helvetica", 12), command=deseleccionar_todas)
btn_deseleccionar_todas.pack(pady=10)

root.mainloop()