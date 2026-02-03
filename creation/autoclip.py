#    _____     _       _____ _ _     
#   |  _  |_ _| |_ ___|     | |_|___ 
#   |     | | |  _| . |   --| | | . |
#   |__|__|___|_| |___|_____|_|_|  _|
#                               |_| 
#
# By Abhishta (github.com/abhishtagatya)
# Improved version

# pip install gTTs
# pip install moviepy
# pip install rich
# pip install pyfiglet

import os
import sys
import shutil
import random
import tempfile
from typing import List, Tuple, Optional
from pathlib import Path


from gtts import gTTS
from moviepy import (
    CompositeVideoClip, CompositeAudioClip,
    VideoFileClip, AudioFileClip, ImageClip, TextClip,
    concatenate_videoclips, concatenate_audioclips
)
from moviepy.video.fx import *
from rich.console import Console
from rich.progress import track
import pyfiglet
from tkinter import filedialog, Tk



class AutoClip:
    def __init__(self):
        self.console = Console()
        self.temp_dir = tempfile.mkdtemp(prefix="autoclip_")
        self.audio_temp_file = os.path.join(self.temp_dir, "temp_audio.mp3")
        
    def __del__(self):
        # Nettoyage des fichiers temporaires à la fin
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.console.print("[dim]Fichiers temporaires nettoyés", style="yellow")
        except Exception as e:
            self.console.print(f"[red]Erreur lors du nettoyage: {e}")

    def generate_speech(self, text: str, lang: str = 'fr', filename: Optional[str] = None) -> str:
        """Generate Speech Audio from gTTS"""
        if not text.strip():
            raise ValueError("Le texte à synthétiser est vide !")
        
        if filename is None:
            filename = os.path.join(self.temp_dir, f"{random.randint(1000, 9999)}_speech.mp3")
        
        try:
            myobj = gTTS(text=text, lang=lang, slow=False, tld='ca')
            myobj.save(filename)
            return filename
        except Exception as e:
            self.console.print(f"[red]Erreur de génération audio: {e}")
            raise
    
    def get_font_path(self):
        """Retourne un chemin de police compatible avec le système"""
        # Vérifier d'abord les polices système courantes
        system_fonts = []
        
        # Windows
        if os.name == 'nt':
            system_fonts = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "C:/Windows/Fonts/segoeui.ttf"
            ]
        # macOS
        elif os.name == 'posix' and sys.platform == 'darwin':
            system_fonts = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Geneva.ttf",
                "/Library/Fonts/Arial.ttf"
            ]
        # Linux
        elif os.name == 'posix':
            system_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/Arial.ttf",
                "/usr/share/fonts/liberation/LiberationSans-Regular.ttf"
            ]
        
        # Vérifier si les polices existent
        for font in system_fonts:
            if os.path.exists(font):
                return font
                
        # Si aucune police n'est trouvée, utiliser une police par défaut de MoviePy
        return None  # MoviePy utilisera sa police par défaut

    def split_text(self, text: str, delimiter: str = '\n') -> List[str]:
        """
        Split the Text
        text: str - Text to split
        delimiter: str - Delimiter of split (default: \n)
        """
        if not text.strip():
            return []
        return [line for line in text.split(delimiter) if line.strip()]

    def generate_audio_text(self, fulltext: List[str]) -> Tuple[List[str], List[TextClip]]:
        """
        Generate Audio and Text from Full Text
        fulltext: List[str] - List of splitted Text
        """
        audio_comp = []
        text_comp = []
        
        if not fulltext:
            self.console.print("[yellow]Attention: Le texte est vide!")
            return [], []

        font_path = self.get_font_path()

        for idx, text in track(enumerate(fulltext), description='Synthétisation audio...'):
            stripped_text = text.strip()
            if not stripped_text:
                continue
                
            try:
                audio_file = os.path.join(self.temp_dir, f"audio_{idx}.mp3")
                self.generate_speech(stripped_text, filename=audio_file)

                audio_clip = AudioFileClip(audio_file)
                audio_duration = audio_clip.duration
                audio_clip.close()

                text_clip = TextClip(
                    text=stripped_text,
                    font_size=50,
                    color='white',
                    font=font_path,  # Utilise la police compatible avec le système
                    size=(1080, 500),
                    method='label'
                ).with_duration(audio_duration)

                audio_comp.append(audio_file)
                text_comp.append(text_clip)
            except Exception as e:
                self.console.print(f"[red]Erreur lors du traitement de la ligne {idx}: {e}")
                # Continuer avec les autres fragments de texte malgré l'erreur
        
        return audio_comp, text_comp

    def clip(self, 
             content: str, 
             video_file: str, 
             outfile: str, 
             image_file: str = '', 
             offset: int = 0, 
             duration: int = 0) -> None:
        """
        Generate the Complete Clip
        content: str - Full content text
        video_file: str - Background video
        outfile: str - Filename of output
        image_file: str - Banner to display
        offset: int - Offset starting point of background video (default: 0)
        duration: int - Limit the video (default: audio length)
        """
        try:
            # Vérifier que les fichiers d'entrée existent
            if not os.path.exists(video_file):
                raise FileNotFoundError(f"Le fichier vidéo {video_file} n'existe pas")
            
            if image_file and not os.path.exists(image_file):
                raise FileNotFoundError(f"Le fichier image {image_file} n'existe pas")
            
            # Vérifier si le contenu est vide
            if not content.strip():
                raise ValueError("Le contenu est vide. Veuillez fournir du texte pour la voix off.")
                
            # Vérifier si le dossier de sortie existe
            outdir = os.path.dirname(os.path.abspath(outfile))
            if outdir and not os.path.exists(outdir):
                os.makedirs(outdir)

            audio_comp, text_comp = self.generate_audio_text(self.split_text(content))
            
            if not audio_comp:
                raise ValueError("Aucun contenu audio n'a été généré.")

            # Combiner les clips audio
            audio_comp_list = []
            for audio_file in track(audio_comp, description='Assemblage audio...'):
                audio_comp_list.append(AudioFileClip(audio_file))
            
            audio_comp_stitch = concatenate_audioclips(audio_comp_list)
            audio_comp_stitch.write_audiofile(self.audio_temp_file, fps=44100)

            audio_duration = audio_comp_stitch.duration
            if duration == 0:
                duration = audio_duration
            
            # S'assurer que la durée ne dépasse pas celle de la vidéo d'arrière-plan
            with VideoFileClip(video_file) as temp_vid:
                max_duration = max(0, int(temp_vid.duration) - offset)
                if offset >= temp_vid.duration:
                    raise ValueError(f"L'offset ({offset}s) est plus grand que la durée de la vidéo ({temp_vid.duration}s)")
                if duration > max_duration:
                    self.console.print(f"[yellow]Attention: La durée demandée ({duration}s) dépasse la durée disponible de la vidéo ({max_duration}s)")
                    duration = max_duration

            # Fermer le clip audio
            audio_comp_stitch.close()

            # Traiter la vidéo
            self.console.print("Traitement de la vidéo en cours...")
            vid_clip = VideoFileClip(video_file).subclipped(offset, offset + duration)
            
            # Redimensionner et recadrer si nécessaire (vérifie d'abord les dimensions)
            if vid_clip.size[0] >= 1980 and vid_clip.size[1] >= 1280:
                vid_clip = vid_clip.resize((1980, 1280))
                vid_clip = vid_clip.crop(x_center=1980 / 2, y_center=1280 / 2, width=720, height=1280)
            else:
                # Adapter au format portrait pour les réseaux sociaux
                aspect_ratio = vid_clip.size[0] / vid_clip.size[1]
                if aspect_ratio > 0.5625:  # Si plus large que 9:16
                    new_height = vid_clip.size[1]
                    new_width = int(new_height * 0.5625)
                    vid_clip = vid_clip.crop(x_center=vid_clip.size[0] / 2, 
                                           y_center=vid_clip.size[1] / 2, 
                                           width=new_width, 
                                           height=new_height)
                else:
                    new_width = vid_clip.size[0]
                    new_height = int(new_width / 0.5625)
                    vid_clip = vid_clip.crop(x_center=vid_clip.size[0] / 2, 
                                           y_center=vid_clip.size[1] / 2, 
                                           width=new_width, 
                                           height=new_height)
                vid_clip = vid_clip.resize((720, 1280))

            # Ajouter l'image si spécifiée
            if image_file:
                try:
                    image_clip = ImageClip(image_file).set_duration(duration)
                    # Ajuster la taille de l'image en fonction de la taille de la vidéo
                    image_width = min(vid_clip.size[0] * 0.8, image_clip.size[0])
                    image_clip = image_clip.resize(width=image_width)
                    image_clip = image_clip.set_position(("center", 'center'))
                    vid_clip = CompositeVideoClip([vid_clip, image_clip])
                except Exception as e:
                    self.console.print(f"[yellow]Avertissement: Impossible d'ajouter l'image: {e}")

            # Ajouter le texte s'il y en a
            if text_comp:
                try:
                    text_position = ('center', int(vid_clip.size[1] * 0.67))  # Position adaptative
                    vid_clip = CompositeVideoClip([vid_clip, concatenate_videoclips(text_comp).set_position(text_position)])
                except Exception as e:
                    self.console.print(f"[yellow]Avertissement: Impossible d'ajouter le texte: {e}")

            # Ajouter l'audio
            vid_clip = vid_clip.set_audio(AudioFileClip(self.audio_temp_file).subclip(0, duration))
            
            # Écrire la vidéo finale
            self.console.print(f"Création du fichier de sortie: {outfile}")
            vid_clip.write_videofile(outfile, audio_codec='aac', threads=4)
            vid_clip.close()
            
            self.console.print(f"[green]Vidéo générée avec succès: {outfile}")

        except Exception as e:
            self.console.print(f"[bold red]Erreur lors de la création du clip: {e}")
            raise


def main():
    # Initialiser Tkinter mais cacher la fenêtre principale
    root = Tk()
    root.withdraw()
    
    autoclip = AutoClip()
    
    console = Console()
    banner = pyfiglet.figlet_format(text='AutoClip', font='rectangles')
    console.print()
    console.print("[bold][red1]" + banner)
    console.print("[dark_red] By Abhishta (github.com/abhishtagatya)")
    console.print("[dark_red] Version améliorée")

    try:
        # Sélection du fichier vidéo
        console.print("\n[blue]Veuillez sélectionner un fichier vidéo d'arrière-plan")
        video_background_file = filedialog.askopenfilename(
            title="Sélectionnez un fichier vidéo",
            filetypes=[("Fichiers vidéo", "*.mkv *.mp4 *.avi *.mov"), ("Tous les fichiers", "*.*")]
        )
        
        if not video_background_file:
            console.print("[red]Aucun fichier vidéo sélectionné. Arrêt du programme.")
            return
            
        # Choix de l'offset
        console.print("[blue]Souhaitez-vous un offset aléatoire pour la vidéo? (o/n)")
        random_offset = input().lower() in ('o', 'oui', 'y', 'yes')
        
        video_background_offset = 0
        if random_offset:
            # Obtenir la durée de la vidéo pour calculer un offset valide
            with VideoFileClip(video_background_file) as clip:
                max_offset = max(0, int(clip.duration) - 30)  # Laisser au moins 30 secondes
            
            if max_offset > 0:
                video_background_offset = random.randint(0, max_offset)
                console.print(f"[blue]Offset aléatoire choisi: {video_background_offset} secondes")
            else:
                console.print("[yellow]La vidéo est trop courte pour un offset aléatoire.")
        else:
            console.print("[blue]Entrez l'offset souhaité en secondes (0 pour commencer au début) :")
            try:
                video_background_offset = int(input())
            except ValueError:
                console.print("[yellow]Valeur invalide, l'offset sera défini à 0.")
                video_background_offset = 0
        
        # Sélection de l'image
        console.print("\n[blue]Souhaitez-vous ajouter une image/logo? (o/n)")
        add_image = input().lower() in ('o', 'oui', 'y', 'yes')
        
        image_banner_file = ""
        if add_image:
            console.print("[blue]Veuillez sélectionner une image")
            image_banner_file = filedialog.askopenfilename(
                title="Sélectionnez une image",
                filetypes=[("Images", "*.jpg *.jpeg *.png *.gif"), ("Tous les fichiers", "*.*")]
            )
            
            if not image_banner_file:
                console.print("[yellow]Aucune image sélectionnée. Continuons sans image.")
        
        # Fichier de sortie
        console.print("\n[blue]Entrez un nom pour le fichier de sortie (ou appuyez sur Entrée pour utiliser 'AutoClip_Out.mp4'):")
        output_file = input().strip()
        if not output_file:
            output_file = "AutoClip_Out.mp4"
        elif not output_file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            output_file += ".mp4"
        
        # Contenu textuel
        console.print("\n[blue]Entrez le texte à synthétiser (terminez par une ligne vide):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        
        content = "\n".join(lines)
        
        if not content.strip():
            console.print("[red]Aucun texte saisi. Veuillez entrer du texte pour la voix off.")
            return
        
        # Confirmation
        console.print("\n[blue]Récapitulatif:")
        console.print(f"- Vidéo: {video_background_file}")
        console.print(f"- Offset: {video_background_offset} secondes")
        console.print(f"- Image: {image_banner_file if image_banner_file else 'Aucune'}")
        console.print(f"- Sortie: {output_file}")
        console.print(f"- Texte: {len(content.strip())} caractères")
        
        console.print("\n[blue]Continuer? (o/n)")
        if input().lower() not in ('o', 'oui', 'y', 'yes'):
            console.print("[yellow]Opération annulée par l'utilisateur.")
            return
        
        console.print("\n\n[light_green]Démarrage de la tâche\n\n")
        
        autoclip.clip(
            content=content, 
            video_file=video_background_file, 
            image_file=image_banner_file,
            outfile=output_file, 
            offset=video_background_offset
        )
        
        console.print("\n\n[light_green]Terminé!")
        
    except Exception as e:
        console.print(f"\n\nUne erreur s'est produite: {e}")
        import traceback
        console.print(traceback.format_exc())
    finally:
        # Assurer que Tkinter est correctement fermé
        root.destroy()


if __name__ == '__main__':
    main()