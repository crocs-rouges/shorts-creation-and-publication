import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import os
import pickle
import logging
from datetime import datetime, time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Configuration du logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='youtube_uploader.log'
)



class TimeSelector(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Variables pour les heures et minutes
        self.hour = tk.StringVar(value="00")
        self.minute = tk.StringVar(value="00")
        
        # Création des spinbox pour heures et minutes
        self.hour_spinbox = ttk.Spinbox(
            self,
            from_=0,
            to=23,
            width=3,
            format="%02.0f",
            textvariable=self.hour,
            wrap=True
        )
        self.hour_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(self, text=":").pack(side=tk.LEFT)
        
        self.minute_spinbox = ttk.Spinbox(
            self,
            from_=0,
            to=59,
            width=3,
            format="%02.0f",
            textvariable=self.minute,
            wrap=True
        )
        self.minute_spinbox.pack(side=tk.LEFT)
        
        # Validation pour garder un format correct
        self.hour_spinbox.bind('<FocusOut>', self._validate)
        self.minute_spinbox.bind('<FocusOut>', self._validate)
    
    def _validate(self, event=None):
        """Valide et formate les valeurs d'heure et de minutes"""
        try:
            hour = int(self.hour.get())
            minute = int(self.minute.get())
            
            hour = max(0, min(hour, 23))
            minute = max(0, min(minute, 59))
            
            self.hour.set(f"{hour:02d}")
            self.minute.set(f"{minute:02d}")
        except ValueError:
            self.hour.set("00")
            self.minute.set("00")
    
    def get_time(self):
        """Retourne un objet time avec l'heure sélectionnée"""
        self._validate()
        return time(int(self.hour.get()), int(self.minute.get()))

class YouTubeUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Uploader (API)")
        self.root.geometry("600x500")
        
        # Variables
        self.video_path = tk.StringVar()
        self.video_title = tk.StringVar()
        self.credentials = None
        self.youtube = None
        self.current_channel = tk.StringVar(value="Aucun compte connecté")
        
        # Création de l'interface
        self.create_widgets()
        
        # Charger le compte actuel s'il existe
        self.load_current_account()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Affichage du compte actuel
        account_frame = ttk.Frame(main_frame)
        account_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Label(account_frame, text="Compte actuel:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(account_frame, textvariable=self.current_channel).pack(side=tk.LEFT)
        
        # Sélection de vidéo
        ttk.Label(main_frame, text="Fichier vidéo:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.video_path, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Parcourir", command=self.browse_video).grid(row=1, column=2, padx=5)
        
        # Titre de la vidéo
        ttk.Label(main_frame, text="Titre:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.video_title, width=40).grid(row=2, column=1, padx=5, pady=5)
        
        # Description
        ttk.Label(main_frame, text="Description:").grid(row=3, column=0, sticky=tk.W)
        self.description_text = tk.Text(main_frame, height=5, width=40)
        self.description_text.grid(row=3, column=1, padx=5, pady=5)
        
        # Frame pour la date et l'heure
        datetime_frame = ttk.Frame(main_frame)
        datetime_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Date de publication
        ttk.Label(main_frame, text="Publication:").grid(row=4, column=0, sticky=tk.W)
        self.date_picker = DateEntry(datetime_frame, width=15)
        self.date_picker.pack(side=tk.LEFT, padx=(0, 10))
        
        # Heure de publication
        self.time_selector = TimeSelector(datetime_frame)
        self.time_selector.pack(side=tk.LEFT)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Configurer l'API", 
                  command=self.setup_api).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Changer de compte",
                  command=self.switch_account).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Uploader la vidéo", 
                  command=self.start_upload).pack(side=tk.LEFT, padx=5)
        
        # Barre de progression
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)

    def load_current_account(self):
        """Charge les informations du compte actuel si elles existent"""
        try:
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
                    if creds and creds.valid:
                        self.credentials = creds
                        self.youtube = build('youtube', 'v3', credentials=creds)
                        self.update_channel_info()
        except Exception as e:
            self.status_label.config(text=f"Erreur lors du chargement du compte: {str(e)}")

    def update_channel_info(self):
        """Met à jour l'affichage des informations du canal"""
        try:
            if self.youtube:
                channel_info = self.youtube.channels().list(
                    part='snippet',
                    mine=True
                ).execute()
                
                if channel_info['items']:
                    channel_title = channel_info['items'][0]['snippet']['title']
                    self.current_channel.set(channel_title)
                else:
                    self.current_channel.set("Aucun canal trouvé")
        except Exception as e:
            self.current_channel.set("Erreur lors de la récupération du canal")
            self.status_label.config(text=f"Erreur: {str(e)}")

    def switch_account(self):
        """Change de compte YouTube en supprimant les credentials actuels"""
        if messagebox.askyesno("Confirmation", 
                             "Voulez-vous vraiment changer de compte ? \n"
                             "Vous devrez vous reconnecter avec un autre compte YouTube."):
            try:
                # Supprimer les credentials actuels
                if os.path.exists('token.pickle'):
                    os.remove('token.pickle')
                
                self.credentials = None
                self.youtube = None
                self.current_channel.set("Aucun compte connecté")
                
                # Relancer la configuration de l'API
                self.setup_api()
            except Exception as e:
                error_msg = f"Erreur lors du changement de compte: {str(e)}"
                self.status_label.config(text=error_msg)
                messagebox.showerror("Erreur", error_msg)

    def browse_video(self):
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Sélectionner une vidéo",
            filetypes=(("Fichiers vidéo", "*.mp4 *.avi *.mkv"), ("Tous les fichiers", "*.*"))
        )
        if filename:
            self.video_path.set(filename)
            
    def setup_api(self):
        try:
            self.status_label.config(text="Configuration de l'API YouTube...")
            self.progress.start()
            
            # Vérification du fichier client_secret.json
            if not os.path.exists('client_secret.json'):
                secret_path = filedialog.askopenfilename(
                    title="Sélectionner le fichier client_secret.json",
                    filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
                )
                if not secret_path:
                    raise Exception("Fichier client_secret.json requis")
                # Copier le fichier sélectionné vers le dossier de travail
                import shutil
                shutil.copy2(secret_path, 'client_secret.json')
            
            SCOPES = [
                'https://www.googleapis.com/auth/youtube.upload',
                'https://www.googleapis.com/auth/youtube.force-ssl'
            ]
            creds = None
            
            # Vérification des credentials existants
            if os.path.exists('token.pickle'):
                try:
                    with open('token.pickle', 'rb') as token:
                        creds = pickle.load(token)
                    self.status_label.config(text="Chargement des credentials existants...")
                except Exception:
                    self.status_label.config(text="Échec du chargement des credentials existants, nouvelle authentification requise...")
                    if os.path.exists('token.pickle'):
                        os.remove('token.pickle')
                    creds = None
            
            # Si pas de credentials valides, les obtenir
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    self.status_label.config(text="Rafraîchissement des credentials...")
                    try:
                        creds.refresh(Request())
                    except Exception:
                        self.status_label.config(text="Échec du rafraîchissement, nouvelle authentification requise...")
                        creds = None
                
                if not creds:
                    self.status_label.config(text="Lancement de l'authentification...")
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                        creds = flow.run_local_server(port=0)
                    except Exception as e:
                        raise Exception(f"Erreur lors de l'authentification: {str(e)}")
                
                # Sauvegarde des nouveaux credentials
                try:
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
                    self.status_label.config(text="Nouveaux credentials sauvegardés...")
                except Exception as e:
                    self.status_label.config(text="Avertissement: Impossible de sauvegarder les credentials")
            
            # Test de la connexion
            self.status_label.config(text="Test de la connexion à l'API YouTube...")
            try:
                self.youtube = build('youtube', 'v3', credentials=creds)
                # Test simple pour vérifier l'accès
                self.youtube.channels().list(part='snippet', mine=True).execute()
                self.credentials = creds
                # Mettre à jour les informations du canal
                self.update_channel_info()
            except Exception as e:
                raise Exception(f"Erreur lors du test de connexion à l'API: {str(e)}")
            
            self.status_label.config(text="API YouTube configurée avec succès!")
            messagebox.showinfo("Succès", "Configuration de l'API YouTube réussie!")
            
        except Exception as e:
            error_msg = f"Erreur de configuration: {str(e)}"
            self.status_label.config(text=error_msg)
            messagebox.showerror("Erreur", error_msg)
        finally:
            self.progress.stop()

    def start_upload(self):
        if not self.youtube:
            messagebox.showerror("Erreur", "Veuillez d'abord configurer l'API YouTube")
            return
            
        if not all([self.video_path.get(), self.video_title.get()]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        file_path = self.video_path.get()
        if not os.path.exists(file_path):
            messagebox.showerror("Erreur", f"Le fichier {file_path} n'existe pas.")
            return
        
        # Vérifier la taille du fichier
        file_size = os.path.getsize(file_path)
        max_upload_size = 128 * 1024 * 1024 * 1024  # 128 Go
        if file_size > max_upload_size:
            messagebox.showerror("Erreur", "Fichier trop volumineux. Limite : 128 Go")
            return
            
        try:
            self.progress.start()
            self.status_label.config(text="Upload en cours...")
            
            publish_date = self.date_picker.get_date()
            publish_time = self.time_selector.get_time()
            publish_datetime = datetime.combine(publish_date, publish_time)
            
            body = {
                'snippet': {
                    'title': self.video_title.get(),
                    'description': self.description_text.get("1.0", tk.END).strip(),
                    'tags': []
                },
                'status': {
                    'privacyStatus': 'private',
                    'publishAt': publish_datetime.isoformat() + 'Z'
                }
            }
            
            media = MediaFileUpload(
                file_path,
                resumable=True,
                chunksize=1024*1024*10  # 10 Mo par chunk
            )
            
            insert_request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    if status:
                        self.status_label.config(
                            text=f"Upload en cours... {int(status.progress() * 100)}%"
                        )
                        self.progress['value'] = int(status.progress() * 100)
                        self.root.update_idletasks()
                except HttpError as e:
                    logging.error(f"Erreur HTTP pendant l'upload: {e}")
                    messagebox.showerror("Erreur HTTP", str(e))
                    break
            
            self.progress.stop()
            if response:
                self.status_label.config(text="Upload terminé avec succès!")
                publish_time_str = publish_datetime.strftime("%d/%m/%Y à %H:%M")
                messagebox.showinfo(
                    "Succès",
                    f"Vidéo uploadée! ID: {response['id']}\nLa vidéo sera publiée le {publish_time_str}."
                )
                logging.info(f"Upload réussi: {response['id']}")
            
        except Exception as e:
            import traceback
            error_message = f"Une erreur est survenue: {str(e)}"
            logging.error(f"Erreur d'upload: {error_message}\n{traceback.format_exc()}")
            self.status_label.config(text=error_message)
            messagebox.showerror("Erreur", f"{error_message}\n\nTrace d'appel :\n{traceback.format_exc()}")
        finally:
            self.progress.stop()
            self.progress['value'] = 0

def main():
    try:
        root = tk.Tk()
        app = YouTubeUploaderGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Erreur fatale", f"Une erreur fatale est survenue: {str(e)}")

if __name__ == "__main__":
    main()