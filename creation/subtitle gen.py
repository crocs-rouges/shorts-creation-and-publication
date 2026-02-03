# Assurez-vous d'avoir installé openai-whisper avec:
# pip install openai-whisper

import os
import shutil
import cv2
import argparse
import textwrap
from moviepy import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm

# Importation explicite de openai-whisper
try:
    import whisper
except ImportError:
    print("Erreur: Impossible d'importer whisper.")
    print("Assurez-vous d'avoir installé le package officiel avec: pip install openai-whisper")
    exit(1)

# Configuration des polices et styles
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.8
FONT_THICKNESS = 2
FONT_COLOR = (255, 255, 255)  # Blanc
FONT_BACKGROUND = (0, 0, 0)   # Noir

class VideoTranscriber:
    def __init__(self, model_path, video_path):
        """
        Initialise le transcripteur vidéo
        
        Args:
            model_path (str): Nom du modèle Whisper (tiny, base, small, medium, large)
            video_path (str): Chemin vers la vidéo à transcrire
        """
        try:
            self.model = whisper.load_model(model_path)
            print(f"Modèle Whisper '{model_path}' chargé avec succès")
        except Exception as e:
            print(f"Erreur lors du chargement du modèle Whisper: {e}")
            raise
            
        self.video_path = video_path
        self.audio_path = os.path.join(os.path.dirname(video_path), "temp_audio.mp3")
        self.text_array = []
        self.fps = 0
        self.char_width = 0
        self.video_width = 0
        self.video_height = 0
    
    def extract_audio(self):
        """Extrait l'audio de la vidéo"""
        try:
            print('Extraction audio...')
            video = VideoFileClip(self.video_path)
            audio = video.audio 
            audio.write_audiofile(self.audio_path, verbose=False, logger=None)
            print('Audio extrait avec succès')
            return True
        except Exception as e:
            print(f"Erreur lors de l'extraction audio: {e}")
            return False
    
    def transcribe_video(self):
        """Transcrit la vidéo et prépare les segments de texte"""
        try:
            print('Transcription de la vidéo...')
            result = self.model.transcribe(self.audio_path)
            
            # Récupérer les dimensions de la vidéo
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                print(f"Erreur: Impossible d'ouvrir la vidéo {self.video_path}")
                return False
                
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Dimensions vidéo: {self.video_width}x{self.video_height}, FPS: {self.fps}")
            
            # Calculer la largeur moyenne des caractères
            sample_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            textsize = cv2.getTextSize(sample_text, FONT, FONT_SCALE, FONT_THICKNESS)[0]
            self.char_width = textsize[0] / len(sample_text)
            
            # Déterminer la largeur maximale pour les sous-titres (80% de la largeur vidéo)
            max_text_width = int(self.video_width * 0.8)
            max_chars_per_line = int(max_text_width / self.char_width)
            
            print(f"Caractères max par ligne: {max_chars_per_line}")
            
            # Traiter chaque segment
            for segment in tqdm(result["segments"]):
                text = segment["text"].strip()
                start_time = segment["start"]
                end_time = segment["end"]
                
                # Convertir les temps en numéros de frames
                start_frame = int(start_time * self.fps)
                end_frame = int(end_time * self.fps)
                
                # Diviser le texte en lignes de taille appropriée
                wrapped_lines = textwrap.wrap(text, width=max_chars_per_line)
                
                if not wrapped_lines:
                    continue
                    
                # Calculer la durée pour chaque ligne
                frames_per_line = max(1, (end_frame - start_frame) // max(1, len(wrapped_lines)))
                
                # Ajouter chaque ligne à text_array
                current_frame = start_frame
                for line in wrapped_lines:
                    line_end_frame = current_frame + frames_per_line
                    if line == wrapped_lines[-1]:  # Dernière ligne
                        line_end_frame = end_frame  # S'assurer que la dernière ligne va jusqu'à la fin du segment
                    
                    self.text_array.append([line, current_frame, line_end_frame])
                    current_frame = line_end_frame
            
            cap.release()
            print(f'Transcription terminée avec {len(self.text_array)} lignes de sous-titres')
            return True
        except Exception as e:
            print(f"Erreur lors de la transcription: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_video(self, output_video_path, temp_folder=None):
        """
        Crée une nouvelle vidéo avec les sous-titres
        
        Args:
            output_video_path (str): Chemin de sortie pour la vidéo
            temp_folder (str, optional): Dossier temporaire pour les frames. Si None, un dossier temporaire sera créé.
        """
        try:
            print('Création de la vidéo avec sous-titres...')
            
            # Créer un dossier temporaire si non spécifié
            if temp_folder is None:
                temp_folder = os.path.join(os.path.dirname(self.video_path), "temp_frames")
            
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)
            
            # Extraction et sous-titrage des frames
            self._process_frames(temp_folder)
            
            # Création de la vidéo à partir des frames
            self._combine_frames_and_audio(temp_folder, output_video_path)
            
            # Nettoyage
            self._cleanup(temp_folder)
            
            print(f'Vidéo créée avec succès: {output_video_path}')
            return True
        except Exception as e:
            print(f"Erreur lors de la création de la vidéo: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _process_frames(self, output_folder):
        """Traite les frames pour ajouter les sous-titres"""
        print('Traitement des frames...')
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise ValueError(f"Impossible d'ouvrir la vidéo {self.video_path}")
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        for frame_num in tqdm(range(total_frames)):
            ret, frame = cap.read()
            if not ret:
                print(f"Avertissement: Impossible de lire la frame {frame_num}/{total_frames}")
                break
            
            # Ajouter des sous-titres si nécessaire
            for segment in self.text_array:
                if frame_num >= segment[1] and frame_num <= segment[2]:
                    text = segment[0]
                    self._add_subtitle_to_frame(frame, text)
                    break
            
            # Enregistrer la frame
            output_path = os.path.join(output_folder, f"{frame_num:06d}.jpg")
            cv2.imwrite(output_path, frame)
            
            # Vérifier que l'image a bien été sauvegardée
            if not os.path.exists(output_path):
                print(f"Avertissement: Échec de sauvegarde de la frame {frame_num}")
        
        cap.release()
    
    def _add_subtitle_to_frame(self, frame, text):
        """Ajoute un sous-titre à une frame"""
        # Calculer la taille du texte
        (text_width, text_height), baseline = cv2.getTextSize(text, FONT, FONT_SCALE, FONT_THICKNESS)
        
        # Positionner le texte en bas de l'écran avec marge
        text_x = max(0, int((frame.shape[1] - text_width) / 2))
        text_y = int(frame.shape[0] * 0.9)  # 90% de la hauteur
        
        # Ajouter un fond semi-transparent pour améliorer la lisibilité
        padding = 10
        
        # S'assurer que les coordonnées sont dans les limites
        x1 = max(0, text_x - padding)
        y1 = max(0, text_y - text_height - padding)
        x2 = min(frame.shape[1] - 1, text_x + text_width + padding)
        y2 = min(frame.shape[0] - 1, text_y + padding)
        
        # Créer l'overlay seulement si les coordonnées sont valides
        if x1 < x2 and y1 < y2:
            overlay = frame.copy()
            cv2.rectangle(
                overlay, 
                (x1, y1), (x2, y2),
                FONT_BACKGROUND, 
                -1
            )
            
            # Fusionner le fond avec transparence
            alpha = 0.6
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Ajouter le texte
        cv2.putText(frame, text, (text_x, text_y), FONT, FONT_SCALE, FONT_COLOR, FONT_THICKNESS)
    
    def _combine_frames_and_audio(self, frames_folder, output_path):
        """Combine les frames et l'audio en une vidéo"""
        print('Combinaison des frames et de l\'audio...')
        
        # Lister et trier les frames
        images = [img for img in os.listdir(frames_folder) if img.endswith(".jpg")]
        if not images:
            raise ValueError(f"Aucune image trouvée dans le dossier {frames_folder}")
            
        images.sort()
        
        # Créer la séquence vidéo
        frame_paths = [os.path.join(frames_folder, image) for image in images]
        clip = ImageSequenceClip(frame_paths, fps=self.fps)
        
        # Ajouter l'audio
        if os.path.exists(self.audio_path):
            audio = AudioFileClip(self.audio_path)
            clip = clip.set_audio(audio)
        else:
            print("Avertissement: Fichier audio non trouvé, la vidéo sera créée sans audio")
        
        # Écrire la vidéo
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    def _cleanup(self, temp_folder):
        """Nettoie les fichiers temporaires"""
        print('Nettoyage des fichiers temporaires...')
        try:
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)
            if os.path.exists(self.audio_path):
                os.remove(self.audio_path)
        except Exception as e:
            print(f"Avertissement lors du nettoyage: {e}")


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Générateur de sous-titres pour vidéos')
    parser.add_argument('--model', type=str, default="base", help='Modèle Whisper (tiny, base, small, medium, large)')
    parser.add_argument('--video', type=str, required=True, help='Chemin vers la vidéo d\'entrée')
    parser.add_argument('--output', type=str, help='Chemin vers la vidéo de sortie')
    
    args = parser.parse_args()
    
    # Si aucun chemin de sortie n'est spécifié, utiliser le même dossier que l'entrée
    if not args.output:
        base_name = os.path.splitext(os.path.basename(args.video))[0]
        args.output = os.path.join(os.path.dirname(args.video), f"{base_name}_subbed.mp4")
    
    # Vérifier si les chemins sont valides
    if not os.path.exists(args.video):
        print(f"Erreur: Le fichier vidéo '{args.video}' n'existe pas.")
        return
    
    try:
        # Créer le transcripteur
        transcriber = VideoTranscriber(args.model, args.video)
        
        # Processus complet
        if transcriber.extract_audio() and transcriber.transcribe_video():
            transcriber.create_video(args.output)
    except Exception as e:
        print(f"Erreur critique: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()