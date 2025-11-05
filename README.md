# YouTube Downloader 2025

Application de bureau en Python (Tkinter) pour télécharger des vidéos ou des playlists YouTube avec `yt-dlp` (ou `youtube-dl` en solution de repli).

## Fonctionnalités principales

- Analyse automatique des URLs (vidéo, playlist, chaîne) et détection de toutes les vidéos associées.
- Téléchargement vidéo avec sélection de qualité (jusqu'à 4K) ou téléchargement audio MP3 uniquement.
- Interface graphique claire avec suivi de la progression totale et par fichier.
- Sauvegarde de l'historique des téléchargements via `downloaded.txt` pour éviter les doublons.

## Prérequis

- Python 3.9 ou supérieur.
- `yt-dlp` (recommandé) ou `youtube-dl` installé dans l'environnement Python.
- FFmpeg pour la conversion audio (nécessaire pour l'extraction MP3).

### Installation des dépendances

```bash
python -m venv .venv
source .venv/bin/activate  # Sous Windows : .venv\\Scripts\\activate
pip install yt-dlp
```

> Astuce : si `yt-dlp` n'est pas disponible, installez `youtube-dl` (`pip install youtube-dl`).

Installez également FFmpeg via votre gestionnaire de paquets (apt, brew, choco, etc.) ou depuis le site officiel : <https://ffmpeg.org/download.html>.

## Lancement de l'application

```bash
python download_youtube_video.py
```

Une fenêtre Tkinter s'ouvre. Collez une ou plusieurs URLs (une par ligne), choisissez la qualité désirée ou l'option « Audio seulement (mp3) », sélectionnez le dossier de sortie puis cliquez sur **Lancer les Téléchargements**.

## Organisation des téléchargements

- Les fichiers sont enregistrés dans le dossier spécifié (par défaut `youtube/`).
- Les téléchargements déjà effectués sont consignés dans `downloaded.txt` pour éviter les doublons lors de futurs lancements.

## Résolution des problèmes

- **Erreur "Veuillez entrer au moins une URL"** : assurez-vous d'avoir collé au moins une URL valide.
- **Blocages ou erreurs réseau** : vérifiez votre connexion Internet ou utilisez un VPN si YouTube est restreint.
- **Conversion audio échouée** : confirmez que FFmpeg est installé et accessible via la variable d'environnement `PATH`.

## Licence

Ce projet n'indique pas encore de licence spécifique. Veillez à respecter les conditions d'utilisation de YouTube et des dépendances.
