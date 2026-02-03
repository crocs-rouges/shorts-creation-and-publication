import requests
from bs4 import BeautifulSoup
from concurrent import futures
from tqdm import tqdm
import argparse
import os
import time
import random
import json
import re
from urllib.parse import urlparse, parse_qs

# Configuration des headers pour simuler un navigateur
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.4',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

# Configuration du parser d'arguments
parser = argparse.ArgumentParser(description="Download-All-Tiktok-Videos: A simple script that downloads TikTok videos concurrently.")
parser.add_argument("--links", default="download/links.txt", help="The path to the .txt file that contains the TikTok links. (Default: links.txt)")
parser.add_argument("--workers", default=3, help="Number of concurrent downloads. (Default: 3)", type=int)
args = parser.parse_args()

# Vérification si le fichier existe
if not os.path.exists(args.links):
    print(f"Le fichier {args.links} n'existe pas!")
    exit(1)

# Lecture des liens TikTok
with open(args.links, "r") as links_file:
    tiktok_links = [link.strip() for link in links_file.readlines() if link.strip()]

# Création du fichier errors.txt s'il n'existe pas
error_path = "download/errors.txt"
with open(error_path, 'w') as error_file:
    pass

def extract_video_id(tiktok_url):
    """Extrait l'ID de la vidéo TikTok à partir de l'URL"""
    # Essayons d'abord avec l'analyse d'URL
    parsed_url = urlparse(tiktok_url)
    path_segments = parsed_url.path.strip('/').split('/')
    
    # Format typique: /@username/video/1234567890
    if len(path_segments) >= 3 and path_segments[-2] == 'video':
        return path_segments[-1]
    
    # Essai avec une expression régulière pour capturer l'ID numérique
    video_id_match = re.search(r'/video/(\d+)', tiktok_url)
    if video_id_match:
        return video_id_match.group(1)
    
    # Dernier recours: utiliser la dernière partie de l'URL
    if path_segments:
        last_segment = path_segments[-1]
        # Si c'est un nombre, c'est probablement l'ID
        if last_segment.isdigit():
            return last_segment
    
    # Si tout échoue, générer un ID basé sur le timestamp
    return f"unknown_{int(time.time())}"

def extract_username(tiktok_url):
    """Extrait le nom d'utilisateur à partir de l'URL TikTok"""
    parsed_url = urlparse(tiktok_url)
    path_segments = parsed_url.path.strip('/').split('/')
    
    # Chercher un segment commençant par @
    for segment in path_segments:
        if segment.startswith('@'):
            return segment
    
    # Chercher avec une expression régulière
    username_match = re.search(r'/@([^/]+)', tiktok_url)
    if username_match:
        return f"@{username_match.group(1)}"
    
    return "unknown_user"

def download_tiktok_video(url):
    """
    Télécharge une vidéo TikTok sans filigrane en utilisant snaptik.app
    """
    try:
        # Service de téléchargement alternatif: ssstik.io via une API rapide
        api_url = "https://ssstik.io/abc?url=dl"
        
        # Préparer les données pour l'API
        form_data = {
            "id": url,
            "locale": "fr",
            "tt": "Y0FOaDQ3"  # Jeton qui peut changer, mettre à jour si nécessaire
        }
        
        headers_ssstik = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Origin": "https://ssstik.io",
            "Referer": "https://ssstik.io/fr",
        }
        
        # Faire la requête pour obtenir la page de téléchargement
        response = requests.post(api_url, headers=headers_ssstik, data=form_data)
        
        if response.status_code != 200:
            # Essayer une autre méthode: tikmate.online
            return download_tiktok_with_tikmate(url)
        
        # Analyser la réponse pour trouver le lien de téléchargement
        soup = BeautifulSoup(response.text, "html.parser")
        download_link = soup.find("a", {"class": "without_watermark"})
        
        if not download_link or not download_link.get("href"):
            download_link = soup.find("a", {"class": "without_watermark_direct"})
        
        if not download_link or not download_link.get("href"):
            for a_tag in soup.find_all("a"):
                if a_tag.get("href") and "download" in a_tag.get("href", ""):
                    download_link = a_tag
                    break
        
        if not download_link or not download_link.get("href"):
            # Si toujours pas de lien, essayer une autre méthode
            return download_tiktok_with_tikmate(url)
        
        # Lien direct pour télécharger la vidéo
        download_url = download_link["href"]
        
        # Retourner l'URL de téléchargement
        return download_url
    
    except Exception as e:
        print(f"Erreur avec ssstik.io: {str(e)}")
        # En cas d'échec, essayer la méthode alternative
        return download_tiktok_with_tikmate(url)

def download_tiktok_with_tikmate(url):
    """
    Méthode alternative utilisant tikmate.online
    """
    try:
        # Première étape: accéder à la page principale pour obtenir les cookies et jetons
        session = requests.Session()
        tikmate_url = "https://tikmate.online/"
        
        response = session.get(tikmate_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        })
        
        # Extraire le token (s'il existe)
        soup = BeautifulSoup(response.text, "html.parser")
        token_input = soup.find("input", {"name": "token"})
        token = token_input["value"] if token_input else ""
        
        # Préparer les données pour l'envoi
        form_data = {
            "url": url,
            "token": token
        }
        
        # Faire la requête pour la page de téléchargement
        download_page = session.post(f"{tikmate_url}download", data=form_data, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": tikmate_url,
            "Referer": tikmate_url,
        })
        
        # Extraire le lien de téléchargement
        soup = BeautifulSoup(download_page.text, "html.parser")
        
        # Chercher les boutons de téléchargement
        download_links = soup.select("a.download-link") or soup.select("a.abutton")
        
        if not download_links:
            # Chercher n'importe quel lien qui pourrait être pour le téléchargement
            for a_tag in soup.find_all("a"):
                href = a_tag.get("href", "")
                if "download" in href or "mp4" in href:
                    download_links = [a_tag]
                    break
        
        if not download_links:
            raise Exception("Impossible de trouver le lien de téléchargement sur tikmate.online")
        
        # Prendre le premier lien (sans filigrane de préférence)
        download_url = download_links[0]["href"]
        
        # Si le lien est relatif, le convertir en absolu
        if not download_url.startswith("http"):
            download_url = f"{tikmate_url.rstrip('/')}{download_url}"
        
        return download_url
    
    except Exception as e:
        # En cas d'échec, renvoyer None et laisser la fonction principale gérer l'erreur
        print(f"Erreur avec tikmate.online: {str(e)}")
        return None

def download(link):
    try:
        # Extraire les informations de la vidéo
        video_id = extract_video_id(link)
        username = extract_username(link)
        
        # Création du nom de dossier
        folder_name : str = username.replace("@", "")
        folder_name : str = "download/video/" + folder_name
        """le folder name est très important dans ce cas là 
        surtout si on doit choisir une destination spécifique
        """
        folder_name : str = "download/video"
        
        # Création du dossier s'il n'existe pas
        if not os.path.exists(folder_name):
            os.makedirs(folder_name, exist_ok=True)
            print(f"Dossier créé: {folder_name}")
            
        file_name = f"{video_id}"
        file_path = f"{folder_name}/{file_name}.mp4"
        
        # Vérifier si le fichier existe déjà
        if os.path.exists(file_path):
            print(f"La vidéo {file_name} existe déjà. Téléchargement ignoré.")
            return
        
        print(f"Recherche du lien de téléchargement pour {link}...")
        
        # Obtenir le lien de téléchargement
        download_url = download_tiktok_video(link)
        
        if not download_url:
            raise Exception("Impossible de trouver un lien de téléchargement valide")
        
        # Téléchargement de la vidéo
        print(f"Téléchargement de {file_name} en cours...")
        
        # Ajouter un délai pour éviter les blocages
        time.sleep(random.uniform(1, 3))
        
        # Télécharger le fichier avec progression
        response = requests.get(download_url, stream=True, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        })
        
        if response.status_code != 200:
            raise Exception(f"Erreur lors du téléchargement: {response.status_code}")
            
        file_size = int(response.headers.get("content-length", 0))
        
        with open(file_path, 'wb') as video_file, tqdm(
            total=file_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
            bar_format='{percentage:3.0f}%|{bar:20}{r_bar}{desc}',
            colour='green',
            desc=f"[{file_name}]"
        ) as progress_bar:
            for data in response.iter_content(chunk_size=1024):
                size = video_file.write(data)
                progress_bar.update(size)
                
        print(f"Téléchargement terminé: {file_path}")
        
    except Exception as e:
        print(f"Erreur lors du téléchargement de {link}: {str(e)}")
        with open(error_path, 'a') as error_file:
            error_file.write(f"{link} - Erreur: {str(e)}\n")

def download_tiktok_main():
    """télécharge les vidéos présente dans le fichier links.txt
    et les place dans le dossier download/video 
    - sans distinction en fonction du nom de l'utilisateur
    - toute les vidéos ont le titre du tiktok et non pas un titre random
    """
    print(f"Début du téléchargement de {len(tiktok_links)} vidéos TikTok...")
    
    if not tiktok_links:
        print("Aucun lien TikTok trouvé dans le fichier spécifié!")
        exit(1)
    
    # Créer un nouveau fichier d'erreurs
    with open(error_path, 'w') as error_file:
        pass
        
    with futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Utiliser list() pour forcer l'exécution de toutes les tâches
        list(executor.map(download, tiktok_links))
        
    print("Téléchargements terminés!")
    print(f"Vérifiez le fichier 'errors.txt' pour les éventuelles erreurs.")

if __name__ == "__main__":
    download_tiktok_main()