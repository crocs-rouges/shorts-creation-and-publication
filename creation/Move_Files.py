import os
import shutil
import glob

def deplacer_videos(nombre_videos : int , 
                    dossier_source : str , 
                    dossier_destination : str = "download/video") -> int:
    """
    Déplace un nombre spécifié de vidéos du dossier source vers le dossier destination.
    
    Args:
        nombre_videos (int): Le nombre de vidéos à déplacer
        dossier_source (str): Le chemin vers le dossier contenant les vidéos à déplacer
        dossier_destination (str): Le chemin vers le dossier où les vidéos seront déplacées
    
    Returns:
        int: Le nombre de vidéos effectivement déplacées
    """
    # Vérifier que les dossiers existent
    if not os.path.isdir(dossier_source):
        raise FileNotFoundError(f"Le dossier source '{dossier_source}' n'existe pas")
    
    # Créer le dossier de destination s'il n'existe pas
    if not os.path.exists(dossier_destination):
        os.makedirs(dossier_destination)
    
    # Extensions vidéo courantes
    extensions_video = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
    
    # Récupérer tous les fichiers vidéo du dossier source
    fichiers_video = []
    for ext in extensions_video:
        fichiers_video.extend(glob.glob(os.path.join(dossier_source, f'*{ext}')))
        fichiers_video.extend(glob.glob(os.path.join(dossier_source, f'*{ext.upper()}')))
    
    # Limiter au nombre demandé
    fichiers_a_deplacer = fichiers_video[:nombre_videos]
    
    # Déplacer les fichiers
    nombre_deplaces = 0
    for fichier in fichiers_a_deplacer:
        nom_fichier = os.path.basename(fichier)
        destination = os.path.join(dossier_destination, nom_fichier)
        
        try:
            shutil.move(fichier, destination)
            nombre_deplaces += 1
            print(f"Déplacé: {nom_fichier}")
        except Exception as e:
            print(f"Erreur lors du déplacement de {nom_fichier}: {e}")
    
    print(f"\n{nombre_deplaces} vidéos déplacées de '{dossier_source}' vers '{dossier_destination}'")
    return nombre_deplaces

# Exemple d'utilisation:
if __name__ == "__main__":
    nombre : int = 5
    dossier_source : str= '/chemin/vers/dossier/source'
    dossier_destination : str = 'download/video'
    deplacer_videos(nombre, dossier_source, dossier_destination )