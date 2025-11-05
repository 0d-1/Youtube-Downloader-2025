import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from os import makedirs, path

# Utilise yt-dlp si dispo (recommandé), sinon youtube-dl
try:
    import yt_dlp as ytdl
except ImportError:
    import youtube_dl as ytdl


def get_items(url, status_callback=None):
    """
    Retourne une liste d'URLs vidéos à partir d'une URL qui peut être :
      - une vidéo unique (watch / youtu.be / shorts)
      - une playlist
      - une page de chaîne (ex: .../@handle/videos)
    """
    if status_callback:
        status_callback("Analyse de l'URL...")

    opts = {
        'extract_flat': True,   # on ne télécharge pas ici, on liste
        'quiet': True,
        'ignoreerrors': True,
    }
    videos = []

    try:
        with ytdl.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return videos

        # Cas playlist/chaîne : 'entries' présent
        if 'entries' in info and info['entries'] is not None:
            for entry in info['entries']:
                if not entry:
                    continue
                vid_url = entry.get('url') or entry.get('webpage_url')
                if vid_url:
                    # Normaliser en URL complète si yt-dlp ne renvoie que l'ID
                    if not vid_url.startswith('http'):
                        vid_url = f"https://www.youtube.com/watch?v={vid_url}"
                    videos.append(vid_url)
        else:
            # Cas vidéo unique
            vid_url = info.get('webpage_url') or info.get('url') or url
            if vid_url and not vid_url.startswith('http'):
                vid_url = f"https://www.youtube.com/watch?v={vid_url}"
            videos.append(vid_url)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'analyser l'URL.\n{e}")
        return []

    if status_callback:
        status_callback(f"{len(videos)} vidéo(s) détectée(s).")
    return videos


def _format_from_quality(quality_label: str) -> str:
    """
    Traduit le choix UI -> sélecteur de format (yt-dlp/youtube-dl)
    """
    mapping = {
        "Auto (meilleure)": "bestvideo+bestaudio/best",
        "2160p (4K)":      "bestvideo[height<=?2160]+bestaudio/best[height<=?2160]",
        "1440p (2K)":      "bestvideo[height<=?1440]+bestaudio/best[height<=?1440]",
        "1080p":           "bestvideo[height<=?1080]+bestaudio/best[height<=?1080]",
        "720p":            "bestvideo[height<=?720]+bestaudio/best[height<=?720]",
        "480p":            "bestvideo[height<=?480]+bestaudio/best[height<=?480]",
        "360p":            "best[height<=?360]",
    }
    return mapping.get(quality_label, "bestvideo+bestaudio/best")


def download_video(url, audio_only=False, quality_label="Auto (meilleure)",
                   output_path=None, progress_callback=None, error_callback=None):
    """
    Télécharge une seule vidéo (ou audio seul).
    """
    try:
        ydl_opts = {
            'progress_hooks': [progress_callback] if progress_callback else [],
            'outtmpl': path.join(output_path or 'youtube', '%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'download_archive': path.join(output_path or 'youtube', 'downloaded.txt'),
        }

        if audio_only:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}
            ]
        else:
            ydl_opts['format'] = _format_from_quality(quality_label)
            # Optionnel : forcer mp4 si tu veux
            # ydl_opts['merge_output_format'] = 'mp4'

        with ytdl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        if error_callback:
            error_callback(e, url)


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Super Downloader")
        self.root.geometry("650x650")
        self.root.columnconfigure(1, weight=1)

        tk.Label(root, text="URL(s) vidéo / playlist / chaîne :").grid(row=0, column=0, padx=10, pady=5, sticky='nw')
        self.url_text = scrolledtext.ScrolledText(root, width=60, height=8, wrap=tk.WORD)
        self.url_text.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky='nsew')
        self.root.rowconfigure(0, weight=1)

        options_frame = tk.LabelFrame(root, text="Options", padx=10, pady=10)
        options_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        options_frame.columnconfigure(1, weight=1)

        self.audio_only_var = tk.BooleanVar()
        audio_cb = tk.Checkbutton(options_frame, text="Audio seulement (mp3)", variable=self.audio_only_var,
                                  command=self._toggle_quality_state)
        audio_cb.grid(row=0, column=0, columnspan=3, sticky='w')

        tk.Label(options_frame, text="Qualité vidéo :").grid(row=1, column=0, pady=5, sticky='w')
        self.quality_var = tk.StringVar(value="Auto (meilleure)")
        self.quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var, state="readonly",
                                          values=[
                                              "Auto (meilleure)",
                                              "2160p (4K)",
                                              "1440p (2K)",
                                              "1080p",
                                              "720p",
                                              "480p",
                                              "360p",
                                          ])
        self.quality_combo.grid(row=1, column=1, pady=5, sticky='we')

        tk.Label(options_frame, text="Dossier de sortie :").grid(row=2, column=0, pady=5, sticky='w')
        self.output_path_entry = tk.Entry(options_frame)
        self.output_path_entry.grid(row=2, column=1, pady=5, sticky='we')
        self.output_path_entry.insert(0, "youtube")
        tk.Button(options_frame, text="Parcourir...", command=self.browse_output_path).grid(
            row=2, column=2, padx=5, pady=5)

        self.download_button = tk.Button(root, text="Lancer les Téléchargements", command=self.start_download_thread)
        self.download_button.grid(row=2, column=0, columnspan=3, padx=10, pady=20)

        progress_frame = tk.LabelFrame(root, text="Progression", padx=10, pady=10)
        progress_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        progress_frame.columnconfigure(1, weight=1)

        tk.Label(progress_frame, text="Progression totale :").grid(row=0, column=0, sticky='w')
        self.overall_progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.overall_progress.grid(row=0, column=1, sticky='we')

        tk.Label(progress_frame, text="Progression du fichier :").grid(row=1, column=0, pady=5, sticky='w')
        self.file_progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.file_progress.grid(row=1, column=1, pady=5, sticky='we')

        self.status_label = tk.Label(root, text="Prêt à télécharger.")
        self.status_label.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky='w')

    def _toggle_quality_state(self):
        if self.audio_only_var.get():
            self.quality_combo.state(["disabled"])
        else:
            self.quality_combo.state(["!disabled"])

    def browse_output_path(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, folder_selected)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes:
                percentage = (d.get('downloaded_bytes', 0) / total_bytes) * 100
                self.file_progress['value'] = percentage
                self.root.update_idletasks()
        elif d['status'] == 'finished':
            self.file_progress['value'] = 100
            self.root.update_idletasks()

    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def on_error(self, error, url):
        print(f"Erreur pour {url}: {error}")

    def download_all_content(self):
        # Récupère toutes les lignes non vides (tu peux coller plusieurs URLs)
        raw = self.url_text.get("1.0", tk.END)
        sources = [u.strip() for u in raw.splitlines() if u.strip()]
        if not sources:
            messagebox.showerror("Erreur", "Veuillez entrer au moins une URL.")
            self.download_button.config(state=tk.NORMAL)
            return

        # Construire la liste finale de vidéos à télécharger (vidéo unique OU liste)
        all_urls = []
        for src in sources:
            items = get_items(src, self.update_status)
            if items:
                all_urls.extend(items)

        if not all_urls:
            messagebox.showinfo("Information", "Aucune vidéo trouvée.")
            self.update_status("Prêt.")
            self.download_button.config(state=tk.NORMAL)
            return

        self.overall_progress['maximum'] = len(all_urls)
        self.overall_progress['value'] = 0

        for i, url in enumerate(all_urls, 1):
            self.update_status(f"Téléchargement {i}/{len(all_urls)}…")
            self.file_progress['value'] = 0
            download_video(
                url=url,
                audio_only=self.audio_only_var.get(),
                quality_label=self.quality_var.get(),
                output_path=self.output_path_entry.get(),
                progress_callback=self.progress_hook,
                error_callback=self.on_error
            )
            self.overall_progress['value'] = i

        messagebox.showinfo("Terminé", f"{len(all_urls)} vidéo(s) téléchargée(s) !")
        self.update_status("Prêt.")
        self.download_button.config(state=tk.NORMAL)

    def start_download_thread(self):
        self.download_button.config(state=tk.DISABLED)
        output_path = self.output_path_entry.get()
        if not output_path:
            messagebox.showerror("Erreur", "Veuillez spécifier un dossier de sortie.")
            self.download_button.config(state=tk.NORMAL)
            return
        makedirs(output_path, exist_ok=True)
        threading.Thread(target=self.download_all_content, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
