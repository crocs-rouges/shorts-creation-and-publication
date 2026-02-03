from plusieurs_fichiers import *
from download.download_tiktok import *
from download.Tiktok_Scrapper import *
import datetime
import os
import time

print("hello")
def allProcess(tiktok_accountname : str , 
         hashtags: list[str],
         num_videos_per_hashtag : int ,
         videos_folder : str ,
         publish_Youtube : bool = False ,
         publish_Tiktok : bool = True,
         ):
    """fonction qui va télécharger un nombre x de vidéos sur tiktok en allant chercher leurs liens
    via la fonction tiktok_scrapper puis les télécharger avec download_tiktok.

    puis en fonction du nombre de vidéos choisi elle va décider d'un intervalle de publication
    pour que les vidéos se publie sur 24h.

    elle sont publier avec le nom du fichier de la vidéo et les hashtags avec lesquels elle a été téléchargée
    puis elle va supprimer les fichiers téléchargés pour éviter la saturation du disque dur.

    Args:
        tiktok_accountname (str): nom du compte tiktok sur lequel on publie les vidéos
        hashtags (list[str]): les hashtags via lesquels on va télécharger les vidéos qui vont etre publier
        num_videos_per_hashtag (int): nombre de vidéos télécharger par hashtags
        videos_folder (str): chemin vers l'emplacement des vidéos pour le téléchargement et la publication
    """
    # Étape 1: Télécharger les liens de vidéos TikTok
    print("Étape 1: Récupération des liens TikTok...")
    # Extraction des hashtags sans le symbole #
    clean_hashtags = [tag.replace('#', '') for tag in hashtags]
    # Utiliser la fonction tiktok_scrapper pour obtenir les liens
    Scrappe_Main(clean_hashtags, num_videos_per_hashtag)
    
    # Étape 2: Télécharger les vidéos
    print("\nÉtape 2: Téléchargement des vidéos...")
    # Télécharger les vidéos à partir des liens
    download_tiktok_main()  # Appel de la fonction main() de download_tiktok.py
    # Attendre un moment pour s'assurer que tous les téléchargements sont terminés
    print("Attente de la fin des téléchargements...")
    time.sleep(5)
    
    # Étape 3: Préparer les vidéos pour la publication
    print("\nÉtape 3: Préparation des vidéos pour la publication...")
    # Trouver toutes les vidéos téléchargées
    all_videos = []
    for root, dirs, files in os.walk(videos_folder):
        for file in files:
            if file.endswith(".mp4"):
                all_videos.append(os.path.join(root, file))
    print(f"Nombre de vidéos téléchargées: {len(all_videos)}")
    intervale : int = 20 // len(all_videos) # renvoie un nombre d'heure entiers
    # pour que l'intervalle de publication soit sur 24 heures 
    start_time_now = datetime.datetime.now() #date et heure réelle
    start_time_now = start_time_now + datetime.timedelta(hours= 1)
    start_time_now = start_time_now.replace(second=0, microsecond=0)
    print(f"intervalle de {intervale} heures entre les vidéo")
    
    # Étape 4: Publier les vidéos avec un intervalle
    print("\nÉtape 4: Publication des vidéos...")
    # Utiliser la fonction upload_videos_from_folder pour planifier les publications
    upload_videos_from_folder(
        folder_path = videos_folder,
        tiktok_accountname = tiktok_accountname,
        default_hashtags = hashtags,
        interval_hours = intervale,
        start_time = start_time_now,
        tiktok = publish_Tiktok,
        youtube = publish_Youtube,
    )
    
    # Étape 5: Nettoyer les fichiers téléchargés
    print("\nÉtape 5: Nettoyage des fichiers téléchargés...")
    try:
        # Supprimer les vidéos du dossier de téléchargement
        for video_path in all_videos:
            if os.path.exists(video_path):
                os.remove(video_path)
                print(f"Supprimé: {video_path}")
        # Supprimer le fichier de liens
        if os.path.exists(links_file):
            os.remove(links_file)
            print(f"Supprimé: {links_file}")
        print("Nettoyage terminé avec succès!")
    except Exception as e:
        print(f"Erreur lors du nettoyage: {str(e)}")
    print("\nProcessus de téléchargement et publication terminé!")



def upload_multiple(all_account : dict[str, list[str]], num_vid : int = 3):
    """fonction qui va pour chaque compte dans le dictionnnaire all_account,
    trouver des vidéos via la fonction tiktok_scrapper et les télécharger via la fonction download_videos,
    puis les publier via la fonction upload_videos_from_folder.

    Args:
        all_account (dict[str, list[str]]): dictionnaire de tout les comptes avec leur hashtags respectifs
        num_vid (int, optional): nombre de vidéos télécharger par hashtags. Defaults to 3.
    """
    print("début de tout")
    for account, hashtags in all_account.items():
        print(f"\nCompte: {account}")
        print(f"Hashtags: {hashtags}")
    
    for account, hashtags in all_account.items():
        print(f"lancement de la procédure pour {account} en utilisant les hashtags {hashtags}")
        allProcess( tiktok_accountname = account, 
            hashtags = hashtags, 
            num_videos_per_hashtag = num_vid,
            videos_folder= folder,
            # publish_Tiktok= True, pas besooin car déjà dans allProcess
            # publish_Youtube = False,
            )
        print(f"fin pour {account}")
    print("fin de tout")

print(f"[bold red] bonjour")
choice : int = 0
tab_account : list[str] = ["urban_beast_mode", "jokemeup", "psychologie_astuce_"]
account_dict : dict[str,list[str]] = {}
account_dict["urban_beast_mode"] = ["parkour","freerun"]
account_dict["jokemeup"] = ["joke","fun","funny","hilarous"]
account_dict["psychologie_astuce_"] = ["psychologie","astuce","focus","motivation"]
print(account_dict)
folder = "download/video"
# upload_multiple(all_account = account_dict , num_vid = 1 )
allProcess(tiktok_accountname = tab_account[choice] ,
           hashtags = account_dict[tab_account[choice]],
           num_videos_per_hashtag = 2,
           videos_folder = folder
           )