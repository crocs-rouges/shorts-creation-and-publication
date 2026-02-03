import os
import datetime
from Tiktok.function import upload_tiktok
from Youtube.YT_upload_API import upload_youtube
from creation.Move_Files import deplacer_videos

def upload_videos_from_folder(folder_path : str, 
                             tiktok_accountname : str = 'crocsrouges',
                             video_title : str = None,
                             default_hashtags : list[str]= ['#parkour', '#calisthenics'],
                             sound_name : str = "",
                             video_description : str= "",
                             video_tags : list[str] = ['parkour', 'calisthenics', "shorts"],
                             video_category_id : str = "42",  # Catégorie 42 pour les shorts
                             interval_hours : int = 1,  # Intervalle en heures entre chaque publication
                             start_time : datetime = None,  # Heure de début pour la première publication
                             youtube : bool = True,
                             tiktok : bool = True,

                             ):
    """
    upload toutes les vidéos d'un dossier sur TikTok et YouTube avec un intervalle de temps.
    
    Args:
        folder_path (str): Chemin vers le dossier contenant les vidéos
        tiktok_accountname (str): Nom du compte TikTok
        video_title (str): Titre de la vidéo
        default_hashtags (list): Hashtags par défaut pour TikTok
        sound_name (str): Nom du son par défaut pour TikTok
        video_description (str): Description par défaut pour YouTube
        video_tags (list): Tags par défaut pour YouTube
        video_category_id (str): ID de catégorie YouTube
        interval_hours (int): Nombre d'heures entre chaque publication (par défaut: 1 heure)
        start_time (datetime): Heure de début pour la première publication (par défaut: heure actuelle)
        youtube(bool) : si oui ou non on publie sur youtube
        tiktok(bool) : publie-t-on sur tiktok true = oui
    return:
        None
    """
    # Vérifier si le dossier existe
    if not os.path.isdir(folder_path):
        print(f"Le dossier {folder_path} n'existe pas.")
        return

    # Extensions vidéo courantes
    video_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.mkv']
    
    # Lister tous les fichiers vidéo dans le dossier
    video_files = [f for f in os.listdir(folder_path) 
                  if os.path.isfile(os.path.join(folder_path, f)) 
                  and os.path.splitext(f)[1].lower() in video_extensions]
    
    if not video_files:
        print(f"Aucun fichier vidéo trouvé dans {folder_path}")
        return
    
    print(f"Trouvé {len(video_files)} fichiers vidéo à télécharger")
    
    # Définir l'heure de début
    if start_time is None:
        try:
            start_time = datetime.datetime.now()
        except:
            print("Erreur lors de l'obtention de la date actuelle")
            start_time = None
    
    # Traiter chaque vidéo
    for i, video_file in enumerate(video_files):
        print(f"publication de la vidéo {i+1} sur {len(video_files)}")
        video_path = os.path.join(folder_path, video_file)
        
        # Générer un titre basé sur le nom du fichier (sans l'extension)
        if video_title == "" or video_title == None:
            base_name = os.path.splitext(video_file)[0]
            """-------------------------------------------
            nom de la vidéo
            ----------------------------------------------
            """
            video_title = f"{base_name}"
        
        
        # Programmer le téléchargement avec l'intervalle spécifié
        if start_time:
            # Ajouter l'intervalle en heures pour chaque vidéo
            publish_time = start_time + datetime.timedelta(hours=interval_hours * i)
            print(f"Publication programmée pour: {publish_time}")
            
            # Extraction du jour du mois pour TikTok
            day_of_month = publish_time.day
            
            # Préparation du format d'heure pour TikTok (minutes en multiple de 5)
            minutes = publish_time.minute
            # Arrondir les minutes au multiple de 5 le plus proche
            minutes = ((minutes + 2) // 5) * 5
            minutes += 5
            if minutes == 60:
                minutes = 0
                new_hour = publish_time.hour + 1
                if new_hour == 24:
                    new_hour = 0
            else:
                new_hour = publish_time.hour
            
            # Format HH:MM pour TikTok
            schedule_time_format = f"{new_hour:02d}:{minutes:02d}"
            
            print(f"Format d'heure TikTok: {schedule_time_format}, jour: {day_of_month}")
        else:
            publish_time = None
            schedule_time_format = None
            day_of_month = None
        
        try:
            # Télécharger sur TikTok
            print(f"Téléchargement sur TikTok: {video_title}")
            
            if tiktok:
                # Si un horaire de publication est défini
                if publish_time:
                    upload_tiktok(video=video_path, 
                                description=video_title, 
                                accountname=tiktok_accountname, 
                                hashtags=default_hashtags,
                                schedule=schedule_time_format,  # Format HH:MM avec minutes en multiple de 5
                                day=day_of_month,  # Jour du mois
                                sound_name= sound_name ,
                                sound_aud_vol= "background",
                                stealth= True,
                                headless= False) 
                    print(f"✅ upload schedule réussi sur tiktok pour {video_file}")
                else:
                    upload_tiktok(video=video_path,
                                description=video_title,
                                accountname=tiktok_accountname,
                                hashtags=default_hashtags,
                                sound_name= sound_name ,
                                sound_aud_vol= "background",
                                copyrightcheck= True,
                                stealth= True,
                                headless= False)
                    print(f"upload direct sur tiktok réussi pour {video_file}")
            
            if youtube:
                try:
                    # Télécharger sur YouTube
                    print(f"Téléchargement sur YouTube: {video_title}")
                    upload_youtube(file_path=video_path, 
                                title=video_title, 
                                description=video_description, 
                                tags=video_tags, 
                                category_id=video_category_id,
                                scheduled_time=publish_time)  # Format datetime complet pour YouTube
                    print(f"✅ Téléchargement réussi sur youtube pour {video_file}")
                except Exception as e:
                    print(f"❌ Erreur lors de l'upload sur youtube de {video_file}: {str(e)}")
                
                print(f"✅ Téléchargement réussi pour {video_file}")
            
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement de {video_file}: {str(e)}")

def calcul_intervale(folder_path : str = "C:/Users/romai/Videos/parkour shorts/upload du jour",
                     sur_24H : bool = False) -> int:
    """fonction qui va calculer le temps qui doit etre mis entre chaque vidéo
    pour que tout le dossier soit publier en 10 jours sur tiktok

    Args:
        folder_path (str): chemin vers le dossier contenant toute les vidéos
        sur_24H (bool): si True, alors on calcule l'intervalle sur 24H au lieu de sur 10 jours

    Returns:
        int: renvoie l'intervale parfait pour publier les vidéos sur 10 jours de tiktok
    """
    # Extensions vidéo courantes
    video_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.mkv']
    
    # Lister tous les fichiers vidéo dans le dossier
    video_files = [f for f in os.listdir(folder_path) 
                  if os.path.isfile(os.path.join(folder_path, f)) 
                  and os.path.splitext(f)[1].lower() in video_extensions]
    
    if sur_24H:
        intervalle = float(24) / total_videos
        print(f"Intervalle parfait pour publier les vidéos sur 24H: {intervalle} vidéo(s)")
        return int(intervalle)
    
    else:
        # Calculate the total number of videos
        total_videos = len(video_files)

        # Define the total duration for publishing in hours (10 days * 24 hours/day)
        total_duration_hours = 10 * 24

        # Calculate the interval in hours between each video
        intervalle_heures = float(total_duration_hours) / total_videos
        print(f"Durée totale de publication (10 jours) : {total_duration_hours} heures")
        print(f"Intervalle parfait pour publier les vidéos sur 10 jours: {intervalle_heures:.2f} heures par vidéo")

        return int(intervalle_heures)

        




# Exemple d'utilisation
def publication_classique():
    # déplacer les vidéos pour le compte sur lequel on publie
    nombre_vids : int = 5
    folder_path : str = "C:/Users/romai/Videos/upload_shorts_tiktok/laugh"

    # Spécifiez le dossier contenant vos vidéos
    # videos_folder = "download/video" 
    videos_folder = "C:/Users/romai/Videos/upload_shorts_tiktok/upload"
    # videos_folder = "C:/Users/romai/Videos/vidéo Upload"

    # deplacer_videos( nombre_vids, folder_path, videos_folder)

    # publier sur les platformes
    youtube : bool = False
    tiktok : bool = True
    
    # Informations pour Tiktok
    # tiktok_accountname = 'urban_beast_mode'
    tiktok_accountname = 'jokemeup'
    # tiktok_accountname = 'psychologie_astuce_'
    # tiktok_accountname = 'crocsrouges'

    tiktok_hashtags = ['#parkour ', '#freerun ', '#urbanbeastmode ']
    tiktok_hashtags = ['#gaming ', '#valorant ', '#Valorant '] # pour les vidéos de gaming
    # tiktok_hashtags = ['#psychologie ', '#astuce ', '#motivation ']
    tiktok_hashtags = ["jokes", "funnytok"] # pour les vidéos d'humour
    
    tiktok_song = "juno"
    predefined_title = ""
    
    # Informations pour Youtube
    youtube_description = "allez voir la vidéo complète déjà disponible sur ma chaine youtube"
    youtube_tags = ["gaming ", "valorant ", "Valorant "]
    youtube_category = "42"  # shorts
    # 20 gaming 22 people & blogs 17 sports 28 science 
    # 27 education 31 animation 42 shorts

    
    # Définir une heure de début spécifique (par exemple, aujourd'hui à 12h00)
    start_time_now : datetime = datetime.datetime.now()
    start_time_now : datetime = start_time_now + datetime.timedelta(days= 1, hours = 1)
    # start_time_now = datetime.datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)

    # intervale = 24  # uploader toutes les x heures
    only_one_day = False
    intervale = calcul_intervale(videos_folder , only_one_day)
    
    # Lancer le téléchargement des vidéos avec un intervalle de 1 heure entre chaque vidéo
    upload_videos_from_folder(
        folder_path = videos_folder,
        tiktok_accountname = tiktok_accountname,
        video_title = predefined_title,
        sound_name = tiktok_song,
        default_hashtags = tiktok_hashtags,
        interval_hours = intervale,
        start_time = start_time_now,
        youtube = youtube,
        tiktok = tiktok,
    )
if __name__ == "__main__":
    publication_classique()