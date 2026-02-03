import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import time
from datetime import timedelta
from Tiktok.function import upload_tiktok
from Youtube.YT_upload_API import upload_youtube
from creation.Move_Files import deplacer_videos

class VideoUploadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Programmation de vidéos TikTok/YouTube - Version Complète")
        self.root.geometry("800x750")
        self.root.resizable(True, True)
        
        # Variables
        self.folder_path = tk.StringVar()
        self.interval_hours = tk.DoubleVar(value=24.0)
        self.start_date = tk.StringVar(value=datetime.datetime.now().strftime("%d/%m/%Y"))
        self.start_time = tk.StringVar(value=datetime.datetime.now().strftime("%H:%M"))
        
        # Variables TikTok
        self.tiktok_account = tk.StringVar(value="crocsrouges")
        self.tiktok_accounts = ["crocsrouges", "urban_beast_mode", "jokemeup", "psychologie_astuce_"]
        self.hashtags = tk.StringVar(value="#parkour,#freerun,#urbanbeastmode")
        self.sound_name = tk.StringVar(value="Pony")
        self.predefined_title = tk.StringVar(value="")
        
        # Variables YouTube
        self.yt_description = tk.StringVar(value="allez voir la vidéo complète déjà disponible sur ma chaine youtube")
        self.yt_tags = tk.StringVar(value="parkour,calisthenics,shorts")
        self.yt_category = tk.StringVar(value="42")  # Shorts par défaut
        
        # Variables pour les cases à cocher
        self.publish_tiktok = tk.BooleanVar(value=True)
        self.publish_youtube = tk.BooleanVar(value=False)
        
        # Variables pour le déplacement de fichiers
        self.move_files = tk.BooleanVar(value=False)
        self.source_folder = tk.StringVar()
        self.nb_videos_to_move = tk.IntVar(value=3)
        
        # Variables pour le calcul automatique d'intervalle  
        self.auto_interval = tk.BooleanVar(value=False)
        self.interval_duration = tk.StringVar(value="10_days")  # "24h" ou "10_days"
        
        self.video_files = []
        
        # Catégories YouTube étendues
        self.category_options = {
            "1": "Film & Animation",
            "2": "Autos & Vehicles", 
            "10": "Music",
            "15": "Pets & Animals",
            "17": "Sports",
            "20": "Gaming",
            "22": "People & Blogs",
            "23": "Comedy",
            "24": "Entertainment",
            "25": "News & Politics",
            "26": "Howto & Style",
            "27": "Education",
            "28": "Science & Technology",
            "31": "Animation",
            "42": "Shorts"
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        # Style
        style = ttk.Style()
        style.configure('TFrame', padding=10)
        style.configure('TButton', padding=5)
        style.configure('TLabel', padding=3)
        
        # Frame principal avec onglets
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame pour les options de publication (au-dessus des onglets)
        publish_frame = ttk.LabelFrame(self.root, text="Options de publication")
        publish_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        ttk.Checkbutton(publish_frame, text="Publier sur TikTok", variable=self.publish_tiktok).pack(side=tk.LEFT, padx=20, pady=5)
        ttk.Checkbutton(publish_frame, text="Publier sur YouTube", variable=self.publish_youtube).pack(side=tk.LEFT, padx=20, pady=5)
        
        # Onglet 1: Configuration des dossiers et déplacement
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Configuration & Déplacement")
        
        # Onglet 2: Planification
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Planification")
        
        # Onglet 3: Configuration TikTok
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="TikTok")
        
        # Onglet 4: Configuration YouTube
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="YouTube")
        
        # Onglet 5: Récapitulatif et lancement
        tab5 = ttk.Frame(notebook)
        notebook.add(tab5, text="Récapitulatif")
        
        # --- Onglet 1: Configuration & Déplacement ---
        # Section déplacement de fichiers
        move_frame = ttk.LabelFrame(tab1, text="Déplacement de vidéos (optionnel)")
        move_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(move_frame, text="Activer le déplacement de fichiers", variable=self.move_files).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(move_frame, text="Dossier source:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(move_frame, textvariable=self.source_folder, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(move_frame, text="Parcourir...", command=self.select_source_folder).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(move_frame, text="Nombre de vidéos à déplacer:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(move_frame, from_=1, to=50, textvariable=self.nb_videos_to_move, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Section sélection des vidéos
        folder_frame = ttk.LabelFrame(tab1, text="Dossier de publication")
        folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(folder_frame, text="Dossier des vidéos à publier:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(folder_frame, text="Parcourir...", command=self.select_folder).grid(row=0, column=2, padx=5, pady=5)
        
        self.video_count_label = ttk.Label(folder_frame, text="Aucune vidéo trouvée")
        self.video_count_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Liste des vidéos
        video_list_frame = ttk.LabelFrame(tab1, text="Vidéos à publier")
        video_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.video_listbox = tk.Listbox(video_list_frame, width=60, height=6)
        scrollbar_videos = ttk.Scrollbar(video_list_frame, orient="vertical")
        scrollbar_videos.config(command=self.video_listbox.yview)
        self.video_listbox.config(yscrollcommand=scrollbar_videos.set)
        
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar_videos.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton pour déplacer les fichiers
        ttk.Button(tab1, text="Déplacer les fichiers sélectionnés", command=self.move_videos).pack(pady=10)
        
        # --- Onglet 2: Planification ---
        # Intervalle automatique
        auto_frame = ttk.LabelFrame(tab2, text="Calcul automatique d'intervalle")
        auto_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(auto_frame, text="Calculer l'intervalle automatiquement", 
                       variable=self.auto_interval, command=self.toggle_auto_interval).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(auto_frame, text="Répartir sur:").grid(row=1, column=0, sticky=tk.W, pady=5)
        interval_combo = ttk.Combobox(auto_frame, textvariable=self.interval_duration, width=15)
        interval_combo['values'] = ["24h", "10_days"]
        interval_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Planification manuelle
        schedule_frame = ttk.LabelFrame(tab2, text="Planification manuelle")
        schedule_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(schedule_frame, text="Intervalle entre publications (heures):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.interval_spinbox = ttk.Spinbox(schedule_frame, from_=0.1, to=168, increment=0.1, 
                                           textvariable=self.interval_hours, width=10)
        self.interval_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(schedule_frame, text="Date de début (JJ/MM/AAAA):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(schedule_frame, textvariable=self.start_date, width=15).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(schedule_frame, text="Heure de début (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(schedule_frame, textvariable=self.start_time, width=15).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(schedule_frame, text="Calculer l'intervalle optimal", command=self.calculate_interval).grid(row=3, column=0, columnspan=2, pady=10)
        
        # --- Onglet 3: TikTok ---
        tiktok_frame = ttk.Frame(tab3)
        tiktok_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(tiktok_frame, text="Compte TikTok:").grid(row=0, column=0, sticky=tk.W, pady=5)
        tiktok_account_dropdown = ttk.Combobox(tiktok_frame, textvariable=self.tiktok_account, width=30)
        tiktok_account_dropdown['values'] = self.tiktok_accounts
        tiktok_account_dropdown.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(tiktok_frame, text="Ajouter compte", command=self.add_tiktok_account).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(tiktok_frame, text="Titre prédéfini (optionnel):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(tiktok_frame, textvariable=self.predefined_title, width=50).grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(tiktok_frame, text="Hashtags (séparés par des virgules):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(tiktok_frame, textvariable=self.hashtags, width=50).grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(tiktok_frame, text="Nom du son:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(tiktok_frame, textvariable=self.sound_name, width=30).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Presets TikTok
        presets_frame = ttk.LabelFrame(tab3, text="Presets rapides")
        presets_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(presets_frame, text="Parkour", command=lambda: self.apply_tiktok_preset("parkour")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(presets_frame, text="Gaming/Valorant", command=lambda: self.apply_tiktok_preset("gaming")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(presets_frame, text="Psychologie", command=lambda: self.apply_tiktok_preset("psycho")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(presets_frame, text="Humour/Jokes", command=lambda: self.apply_tiktok_preset("humor")).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(tiktok_frame, text="Note: Les heures TikTok seront arrondies aux multiples de 5 minutes", 
                 font=("Arial", 9, "italic")).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=15)
        
        # --- Onglet 4: YouTube ---
        youtube_frame = ttk.Frame(tab4)
        youtube_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(youtube_frame, text="Description:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.yt_desc_text = tk.Text(youtube_frame, width=50, height=4)
        self.yt_desc_text.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.yt_desc_text.insert(tk.END, self.yt_description.get())
        
        ttk.Label(youtube_frame, text="Tags (séparés par des virgules):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(youtube_frame, textvariable=self.yt_tags, width=50).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(youtube_frame, text="Catégorie:").grid(row=2, column=0, sticky=tk.W, pady=5)
        category_dropdown = ttk.Combobox(youtube_frame, textvariable=self.yt_category, width=40)
        category_dropdown['values'] = [f"{k} - {v}" for k, v in self.category_options.items()]
        category_dropdown.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.category_label = ttk.Label(youtube_frame, text=f"Catégorie: {self.category_options[self.yt_category.get()]}")
        self.category_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        def update_category_label(*args):
            cat_id = self.yt_category.get().split(" - ")[0] if " - " in self.yt_category.get() else self.yt_category.get()
            if cat_id in self.category_options:
                self.category_label.config(text=f"Catégorie: {self.category_options[cat_id]}")
                self.yt_category.set(cat_id)
        
        self.yt_category.trace('w', update_category_label)
        
        # --- Onglet 5: Récapitulatif ---
        recap_frame = ttk.Frame(tab5)
        recap_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(recap_frame, text="Récapitulatif de la programmation:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        self.recap_text = tk.Text(recap_frame, width=70, height=15, wrap=tk.WORD)
        recap_scrollbar = ttk.Scrollbar(recap_frame, orient="vertical")
        recap_scrollbar.config(command=self.recap_text.yview)
        self.recap_text.config(yscrollcommand=recap_scrollbar.set)
        
        self.recap_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        recap_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recap_text.config(state=tk.DISABLED)
        
        # Frame pour les boutons de contrôle
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="Rafraîchir le récapitulatif", command=self.update_recap).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🚀 LANCER LA PROGRAMMATION", command=self.schedule_videos).pack(side=tk.RIGHT, padx=5)
    
    def select_source_folder(self):
        """Sélectionne le dossier source pour le déplacement"""
        folder_path = filedialog.askdirectory(title="Sélectionnez le dossier source des vidéos")
        if folder_path:
            self.source_folder.set(folder_path)
    
    def select_folder(self):
        """Sélectionne le dossier de publication"""
        folder_path = filedialog.askdirectory(title="Sélectionnez le dossier de publication")
        if folder_path:
            self.folder_path.set(folder_path)
            self.update_video_list(folder_path)
    
    def update_video_list(self, folder_path):
        """Met à jour la liste des vidéos"""
        video_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.mkv']
        self.video_files = [f for f in os.listdir(folder_path) 
                           if os.path.isfile(os.path.join(folder_path, f)) 
                           and os.path.splitext(f)[1].lower() in video_extensions]
        
        self.video_count_label.config(text=f"{len(self.video_files)} vidéo(s) trouvée(s)")
        
        self.video_listbox.delete(0, tk.END)
        for video in self.video_files:
            self.video_listbox.insert(tk.END, video)
        
        self.update_recap()
    
    def move_videos(self):
        """Déplace les vidéos du dossier source vers le dossier de publication"""
        if not self.move_files.get():
            messagebox.showwarning("Attention", "Le déplacement de fichiers n'est pas activé.")
            return
        
        if not self.source_folder.get() or not self.folder_path.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner les dossiers source et de destination.")
            return
        
        try:
            deplacer_videos(self.nb_videos_to_move.get(), self.source_folder.get(), self.folder_path.get())
            messagebox.showinfo("Succès", f"{self.nb_videos_to_move.get()} vidéos déplacées avec succès!")
            self.update_video_list(self.folder_path.get())
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du déplacement: {str(e)}")
    
    def toggle_auto_interval(self):
        """Active/désactive le calcul automatique d'intervalle"""
        if self.auto_interval.get():
            self.interval_spinbox.config(state='disabled')
            self.calculate_interval()
        else:
            self.interval_spinbox.config(state='normal')
    
    def calculate_interval(self):
        """Calcule l'intervalle optimal basé sur le nombre de vidéos"""
        if not self.folder_path.get() or not self.video_files:
            messagebox.showwarning("Attention", "Sélectionnez d'abord un dossier avec des vidéos.")
            return
        
        total_videos = len(self.video_files)
        
        if self.interval_duration.get() == "24h":
            interval = 24.0 / total_videos if total_videos > 0 else 1.0
            duration_text = "24 heures"
        else:  # 10_days
            interval = (10 * 24.0) / total_videos if total_videos > 0 else 24.0
            duration_text = "10 jours"
        
        self.interval_hours.set(round(interval, 2))
        messagebox.showinfo("Calcul d'intervalle", 
                           f"Intervalle calculé: {interval:.2f} heures\n"
                           f"Pour répartir {total_videos} vidéos sur {duration_text}")
    
    def add_tiktok_account(self):
        """Ajoute un nouveau compte TikTok"""
        new_account = simpledialog.askstring("Nouveau compte", "Entrez le nom du nouveau compte TikTok:")
        if new_account and new_account.strip():
            if new_account not in self.tiktok_accounts:
                self.tiktok_accounts.append(new_account)
                self.tiktok_account.set(new_account)
                messagebox.showinfo("Succès", f"Compte @{new_account} ajouté!")
            else:
                messagebox.showwarning("Attention", f"Le compte @{new_account} existe déjà.")
    
    def apply_tiktok_preset(self, preset_type):
        """Applique des presets TikTok prédéfinis"""
        presets = {
            "parkour": {
                "account": "urban_beast_mode",
                "hashtags": "#parkour,#freerun,#urbanbeastmode",
                "sound": "Pony"
            },
            "gaming": {
                "account": "urban_beast_mode", 
                "hashtags": "#gaming,#valorant,#Valorant",
                "sound": ""
            },
            "psycho": {
                "account": "psychologie_astuce_",
                "hashtags": "#psychologie,#astuce,#motivation",
                "sound": ""
            },
            "humor": {
                "account": "jokemeup",
                "hashtags": "#jokes,#humor,#funny,#prank",
                "sound": "Pony"
            }
        }
        
        if preset_type in presets:
            preset = presets[preset_type]
            self.tiktok_account.set(preset["account"])
            self.hashtags.set(preset["hashtags"])
            self.sound_name.set(preset["sound"])
            messagebox.showinfo("Preset appliqué", f"Configuration {preset_type.title()} appliquée!")
    
    def format_time_for_tiktok(self, dt):
        """Formate le temps pour TikTok (minutes multiples de 5)"""
        minutes = dt.minute
        minutes = ((minutes + 2) // 5) * 5
        
        if minutes == 60:
            minutes = 0
            new_hour = dt.hour + 1
            if new_hour == 24:
                new_hour = 0
        else:
            new_hour = dt.hour
        
        schedule_format = f"{new_hour:02d}:{minutes:02d}"
        day_of_month = dt.day
        
        return schedule_format, day_of_month
    
    def update_recap(self):
        """Met à jour le récapitulatif"""
        self.recap_text.config(state=tk.NORMAL)
        self.recap_text.delete("1.0", tk.END)
        
        if not self.folder_path.get() or not self.video_files:
            self.recap_text.insert(tk.END, "Veuillez sélectionner un dossier contenant des vidéos.")
            self.recap_text.config(state=tk.DISABLED)
            return
        
        try:
            # Parse date et heure
            day, month, year = map(int, self.start_date.get().split('/'))
            hour, minute = map(int, self.start_time.get().split(':'))
            start_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
            
            interval_hours = self.interval_hours.get()
            yt_description = self.yt_desc_text.get("1.0", tk.END).strip()
            
            # Affichage du récapitulatif
            self.recap_text.insert(tk.END, f"📁 Dossier : {self.folder_path.get()}\n")
            self.recap_text.insert(tk.END, f"🎬 Nombre de vidéos : {len(self.video_files)}\n")
            self.recap_text.insert(tk.END, f"⏰ Intervalle : {interval_hours} heure(s)\n")
            self.recap_text.insert(tk.END, f"📅 Début : {start_time.strftime('%d/%m/%Y à %H:%M')}\n\n")
            
            # Plateformes
            platforms = []
            if self.publish_tiktok.get():
                platforms.append("TikTok")
            if self.publish_youtube.get():
                platforms.append("YouTube")
            
            if not platforms:
                self.recap_text.insert(tk.END, "⚠️ ATTENTION: Aucune plateforme sélectionnée! ⚠️\n\n")
            else:
                self.recap_text.insert(tk.END, f"🚀 Plateformes : {', '.join(platforms)}\n\n")
            
            # Configuration TikTok
            if self.publish_tiktok.get():
                self.recap_text.insert(tk.END, f"📱 TikTok - Compte : @{self.tiktok_account.get()}\n")
                hashtags_list = [tag.strip() for tag in self.hashtags.get().split(',')]
                self.recap_text.insert(tk.END, f"📱 TikTok - Hashtags : {', '.join(hashtags_list)}\n")
                if self.sound_name.get():
                    self.recap_text.insert(tk.END, f"📱 TikTok - Son : {self.sound_name.get()}\n")
                self.recap_text.insert(tk.END, "\n")
            
            # Configuration YouTube
            if self.publish_youtube.get():
                yt_tags_list = [tag.strip() for tag in self.yt_tags.get().split(',')]
                cat_id = self.yt_category.get()
                cat_name = self.category_options.get(cat_id, "Inconnu")
                
                self.recap_text.insert(tk.END, f"📺 YouTube - Description : {yt_description[:50]}{'...' if len(yt_description) > 50 else ''}\n")
                self.recap_text.insert(tk.END, f"📺 YouTube - Tags : {', '.join(yt_tags_list)}\n")
                self.recap_text.insert(tk.END, f"📺 YouTube - Catégorie : {cat_id} - {cat_name}\n\n")
            
            # Planification détaillée
            self.recap_text.insert(tk.END, "📋 PLANIFICATION DES VIDÉOS :\n")
            self.recap_text.insert(tk.END, "=" * 60 + "\n")
            
            current_time = start_time
            for i, video_file in enumerate(self.video_files):
                video_title = self.predefined_title.get() if self.predefined_title.get() else os.path.splitext(video_file)[0]
                tiktok_time, tiktok_day = self.format_time_for_tiktok(current_time)
                
                self.recap_text.insert(tk.END, f"{i+1:2d}. {video_file}\n")
                self.recap_text.insert(tk.END, f"     📱 TikTok: {tiktok_time} (jour {tiktok_day})\n")
                if self.publish_youtube.get():
                    self.recap_text.insert(tk.END, f"     📺 YouTube: {current_time.strftime('%H:%M')}\n")
                self.recap_text.insert(tk.END, f"     📝 Titre: {video_title}\n")
                self.recap_text.insert(tk.END, "\n")
                
                current_time += timedelta(hours=interval_hours)
            
            # Calcul de la durée totale
            end_time = start_time + timedelta(hours=interval_hours * (len(self.video_files) - 1))
            total_duration = end_time - start_time
            
            self.recap_text.insert(tk.END, "=" * 60 + "\n")
            self.recap_text.insert(tk.END, f"🏁 Fin prévue : {end_time.strftime('%d/%m/%Y à %H:%M')}\n")
            self.recap_text.insert(tk.END, f"⏱️ Durée totale : {total_duration.days} jour(s) et {total_duration.seconds//3600} heure(s)\n")
            
        except Exception as e:
            self.recap_text.insert(tk.END, f"Erreur dans le récapitulatif : {str(e)}")
        
        self.recap_text.config(state=tk.DISABLED)
    
    def schedule_videos(self):
        """Lance la programmation des vidéos"""
        if not self.folder_path.get() or not self.video_files:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier contenant des vidéos.")
            return
        
        if not self.publish_tiktok.get() and not self.publish_youtube.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins une plateforme de publication.")
            return
        
        try:
            # Parse date et heure de début
            day, month, year = map(int, self.start_date.get().split('/'))
            hour, minute = map(int, self.start_time.get().split(':'))
            start_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
            
            interval_hours = self.interval_hours.get()
            
            # Récupération des paramètres YouTube
            yt_description = self.yt_desc_text.get("1.0", tk.END).strip()
            yt_tags_list = [tag.strip() for tag in self.yt_tags.get().split(',') if tag.strip()]
            yt_category = self.yt_category.get()
            
            # Récupération des paramètres TikTok
            hashtags_list = [tag.strip() for tag in self.hashtags.get().split(',') if tag.strip()]
            
            # Confirmation
            platforms = []
            if self.publish_tiktok.get():
                platforms.append("TikTok")
            if self.publish_youtube.get():
                platforms.append("YouTube")
            
            confirmation = messagebox.askyesno(
                "Confirmation", 
                f"Êtes-vous sûr de vouloir programmer {len(self.video_files)} vidéos sur {', '.join(platforms)} ?\n\n"
                f"Début: {start_time.strftime('%d/%m/%Y à %H:%M')}\n"
                f"Intervalle: {interval_hours} heure(s)\n\n"
                f"Cette action va créer tous les programmes de publication."
            )
            
            if not confirmation:
                return
            
            # Création d'une fenêtre de progression
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Programmation en cours...")
            progress_window.geometry("400x200")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ttk.Label(progress_window, text="Programmation des vidéos...")
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, length=300, mode='determinate')
            progress_bar.pack(pady=10)
            progress_bar['maximum'] = len(self.video_files)
            
            status_label = ttk.Label(progress_window, text="")
            status_label.pack(pady=10)
            
            log_text = tk.Text(progress_window, height=6, width=50)
            log_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
            
            progress_window.update()
            
            # Programmation des vidéos
            current_time = start_time
            scheduled_count = 0
            errors = []
            
            for i, video_file in enumerate(self.video_files):
                video_path = os.path.join(self.folder_path.get(), video_file)
                video_title = self.predefined_title.get() if self.predefined_title.get() else os.path.splitext(video_file)[0]
                
                status_label.config(text=f"Programmation: {video_file}")
                progress_window.update()
                
                try:
                    # Publication TikTok
                    if self.publish_tiktok.get():
                        tiktok_time, tiktok_day = self.format_time_for_tiktok(current_time)
                        
                        # Appel de la fonction upload_tiktok
                        result = upload_tiktok(
                            video_path=video_path,
                            video_title=video_title,
                            hashtags_list=hashtags_list,
                            schedule_format=tiktok_time,
                            day_of_month=tiktok_day,
                            account_name=self.tiktok_account.get(),
                            sound_name=self.sound_name.get()
                        )
                        
                        if result:
                            log_text.insert(tk.END, f"✅ TikTok: {video_file} programmé pour {tiktok_time}\n")
                        else:
                            log_text.insert(tk.END, f"❌ TikTok: Erreur pour {video_file}\n")
                            errors.append(f"TikTok - {video_file}")
                    
                    # Publication YouTube
                    if self.publish_youtube.get():
                        # Appel de la fonction upload_youtube
                        result = upload_youtube(
                            video_path=video_path,
                            title=video_title,
                            description=yt_description,
                            tags=yt_tags_list,
                            category_id=yt_category,
                            scheduled_time=current_time
                        )
                        
                        if result:
                            log_text.insert(tk.END, f"✅ YouTube: {video_file} programmé pour {current_time.strftime('%H:%M')}\n")
                        else:
                            log_text.insert(tk.END, f"❌ YouTube: Erreur pour {video_file}\n")
                            errors.append(f"YouTube - {video_file}")
                    
                    scheduled_count += 1
                    
                except Exception as e:
                    error_msg = f"Erreur pour {video_file}: {str(e)}"
                    log_text.insert(tk.END, f"❌ {error_msg}\n")
                    errors.append(error_msg)
                
                # Mise à jour de la barre de progression
                progress_bar['value'] = i + 1
                log_text.see(tk.END)
                progress_window.update()
                
                # Délai entre les programmations pour éviter la surcharge
                time.sleep(0.5)
                
                current_time += timedelta(hours=interval_hours)
            
            # Affichage du résultat final
            progress_label.config(text="Programmation terminée!")
            status_label.config(text=f"{scheduled_count}/{len(self.video_files)} vidéos programmées")
            
            # Ajout d'un bouton pour fermer
            close_button = ttk.Button(progress_window, text="Fermer", 
                                     command=progress_window.destroy)
            close_button.pack(pady=10)
            
            # Message de résumé
            if errors:
                error_summary = "\n".join(errors[:5])  # Limite à 5 erreurs pour l'affichage
                if len(errors) > 5:
                    error_summary += f"\n... et {len(errors) - 5} autres erreurs"
                
                messagebox.showwarning(
                    "Programmation terminée avec erreurs",
                    f"Programmation terminée!\n\n"
                    f"✅ Succès: {scheduled_count - len(errors)}/{len(self.video_files)}\n"
                    f"❌ Erreurs: {len(errors)}\n\n"
                    f"Principales erreurs:\n{error_summary}"
                )
            else:
                messagebox.showinfo(
                    "Succès!",
                    f"Toutes les vidéos ont été programmées avec succès!\n\n"
                    f"📁 {len(self.video_files)} vidéos programmées\n"
                    f"🚀 Plateformes: {', '.join(platforms)}\n"
                    f"📅 Début: {start_time.strftime('%d/%m/%Y à %H:%M')}"
                )
        
        except ValueError as e:
            messagebox.showerror("Erreur de format", 
                               "Vérifiez le format de la date (JJ/MM/AAAA) et de l'heure (HH:MM).")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la programmation: {str(e)}")

def main():
    root = tk.Tk()
    app = VideoUploadApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()