from playwright.sync_api import sync_playwright
import json
import time
import subprocess
import pkg_resources
import requests
from PIL import Image
import sys
import os
import warnings
import datetime
from pathlib import Path
warnings.simplefilter("ignore")

cookie_path = "cookies/IG_cookies"

def check_for_updates():
    """Vérifie les mises à jour (placeholder pour maintenant)"""
    try:
        print("Vérification des mises à jour...")
        # Implémentation future pour vérifier les mises à jour du package
    except:
        time.sleep(0.1)

def login_warning(accountname):
    print(f"NO COOKIES FILE FOUND FOR ACCOUNT {accountname}, PLEASE LOG-IN TO {accountname} WHEN PROMPTED")

def save_cookies(cookies, accountname):
    cookie_file = f'{cookie_path}_{accountname}.json'
    with open(cookie_file, 'w') as file:
        json.dump(cookies, file, indent=4)

def check_expiry(accountname):
    cookie_file = f'{cookie_path}_{accountname}.json'
    
    if not os.path.exists(cookie_file):
        return True
    
    try:
        with open(cookie_file, 'r') as file:
            cookies = json.load(file)
        
        current_time = int(time.time())
        cookies_expire = []
        expired = False
        
        for cookie in cookies:
            if cookie['name'] in ['sessionid', 'csrftoken', 'ds_user_id']:
                expiry = cookie.get('expires')
                if not expiry:
                    expiry = cookie.get('expirationDate')
                if expiry:
                    cookies_expire.append(expiry < current_time)
        
        if cookies_expire and all(cookies_expire):
            expired = True
        
        return expired
    except:
        return True

def read_cookies(cookies_path):
    cookie_read = False
    try:
        with open(cookies_path, 'r') as cookiefile:
            cookies = json.load(cookiefile)

        for cookie in cookies:
            if cookie.get('sameSite') not in ['Strict', 'Lax', 'None']:
                cookie['sameSite'] = 'Lax'

        cookie_read = True
    except:
        sys.exit("ERROR: CANT READ COOKIES FILE")
    
    return cookies, cookie_read

def wait_for_upload_completion(page, timeout=300):
    """Attend que l'upload soit terminé en surveillant les éléments de progression"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Vérifier si le bouton "Partager" est disponible
            if page.locator('button:has-text("Partager")').is_visible():
                return True
            
            # Vérifier si le bouton "Share" est disponible (anglais)
            if page.locator('button:has-text("Share")').is_visible():
                return True
            
            # Vérifier les indicateurs de progression
            if page.locator('[role="progressbar"]').is_visible():
                time.sleep(2)
                continue
            
            # Vérifier les messages d'erreur
            if page.locator('text="Une erreur s\'est produite"').is_visible():
                return False
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Erreur lors de l'attente: {e}")
            time.sleep(1)
    
    return False

def handle_instagram_captcha(page):
    """Gère les captchas Instagram basiques"""
    try:
        # Vérifier s'il y a un captcha
        if page.locator('text="Confirmer votre identité"').is_visible():
            print("Captcha détecté. Intervention manuelle requise.")
            input("Veuillez résoudre le captcha manuellement et appuyer sur Entrée pour continuer...")
            return True
        
        # Vérifier d'autres types de vérifications
        if page.locator('text="Nous avons détecté une activité inhabituelle"').is_visible():
            print("Vérification de sécurité détectée. Intervention manuelle requise.")
            input("Veuillez compléter la vérification et appuyer sur Entrée pour continuer...")
            return True
            
        return False
    except:
        return False

def validate_proxy(proxy):
    """Valide la configuration du proxy"""
    if not proxy:
        return

    if not isinstance(proxy, dict):
        raise ValueError("Proxy must be a dictionary.")

    if "server" not in proxy or not isinstance(proxy["server"], str):
        raise ValueError("Proxy must contain a 'server' key with a string value.")

    try:
        proxies = {
            "http": f'http://{proxy["server"]}/',
            "https": f'https://{proxy["server"]}/',
        }
        if proxy.get("username"):
            proxies = {
                "http": f'http://{proxy.get("username")}:{proxy.get("password")}@{proxy["server"]}/',
                "https": f'https://{proxy.get("username")}:{proxy.get("password")}@{proxy["server"]}/',
            }

        response = requests.get("https://www.google.com", proxies=proxies, timeout=10)
        if response.status_code == 200:
            print("Proxy is valid!")
        else:
            raise ValueError(f"Proxy test failed with status code: {response.status_code}")
    except Exception as e:
        raise ValueError(f"Invalid proxy configuration: {e}")

def upload_instagram(video: str, description: str, accountname: str, 
                    schedule: str = None, day: int = None,
                    suppressprint: bool = False, headless: bool = True, 
                    stealth: bool = False, proxy: dict = None,
                    story_mode: bool = False):
    """
    UPLOADS VIDEO TO INSTAGRAM
    --------------------------------------------------------------------------------
    video (str) -> path to video to upload
    description (str) -> description/caption for video
    accountname (str) -> account to upload on
    schedule (str)(opt) -> format HH:MM, your local time to upload video
    day (int)(opt) -> day to schedule video for (not supported by Instagram directly)
    suppressprint (bool)(opt) -> True means function doesn't print anything
    headless (bool)(opt) -> run in headless mode or not
    stealth (bool)(opt) -> will wait second(s) before each operation
    proxy (dict)(opt) -> proxy server to run code on
    story_mode (bool)(opt) -> upload as story instead of post
    --------------------------------------------------------------------------------
    """
    
    cookie_full_path = f"{cookie_path}_{accountname}.json"
    
    try:
        check_for_updates()
    except:
        time.sleep(0.1)

    try:
        validate_proxy(proxy)
    except Exception as e:
        sys.exit(f'Error validating proxy: {e}')

    retries = 0
    cookie_read = False

    if accountname is None:
        sys.exit("PLEASE ENTER NAME OF ACCOUNT TO POST ON")

    # Vérifier et charger les cookies
    if os.path.exists(cookie_full_path):
        cookies, cookie_read = read_cookies(cookies_path=cookie_full_path)
        expired = check_expiry(accountname=accountname)
        if expired:
            os.remove(cookie_full_path)
            print(f"COOKIES EXPIRED FOR ACCOUNT {accountname}, PLEASE LOG-IN AGAIN")
            cookie_read = False
    
    if not cookie_read:
        login_warning(accountname=accountname)
        # Note: Vous devrez implémenter la création automatique de cookies
        # Pour l'instant, demander à l'utilisateur de se connecter manuellement
        print("Please login manually and save cookies using browser dev tools")
        sys.exit("Manual login required for first time setup")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, proxy=proxy)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        context.add_cookies(cookies)
        page = context.new_page()
        
        # URL Instagram
        if story_mode:
            url = 'https://www.instagram.com/stories/new/'
        else:
            url = 'https://www.instagram.com/'

        if not suppressprint:
            print(f"Uploading to Instagram account '{accountname}'")

        # Naviguer vers Instagram
        while retries < 3:
            try:
                page.goto(url, timeout=30000)
                break
            except:
                retries += 1
                time.sleep(5)
                if retries == 3:
                    sys.exit("ERROR: Instagram page failed to load")

        # Gérer les éventuels captchas ou vérifications
        time.sleep(2)
        handle_instagram_captcha(page)

        try:
            # Cliquer sur le bouton "Créer" ou "+"
            if page.locator('[aria-label="Nouveau post"]').is_visible():
                if stealth:
                    time.sleep(2)
                page.locator('[aria-label="Nouveau post"]').click()
            elif page.locator('text="Créer"').is_visible():
                if stealth:
                    time.sleep(2)
                page.locator('text="Créer"').click()
            elif page.locator('svg[aria-label="Nouveau post"]').is_visible():
                if stealth:
                    time.sleep(2)
                page.locator('svg[aria-label="Nouveau post"]').click()
            else:
                # Essayer avec le sélecteur plus générique
                page.locator('[role="menuitem"]:has-text("Créer")').click()
                
        except Exception as e:
            print(f"Could not find create button: {e}")
            # Essayer une approche alternative
            page.keyboard.press("c")  # Raccourci clavier pour créer

        time.sleep(2)

        try:
            # Upload du fichier vidéo
            if not suppressprint:
                print("Uploading video file...")
            
            # Trouver l'input file
            file_input = page.locator('input[type="file"][accept*="video"]')
            if not file_input.is_visible():
                file_input = page.locator('input[type="file"]')
            
            file_input.set_input_files(video)
            
            if not suppressprint:
                print("Video uploaded, waiting for processing...")
            
        except Exception as e:
            sys.exit(f"ERROR: Failed to upload video file: {e}")

        # Attendre le traitement de la vidéo
        time.sleep(5)

        try:
            # Cliquer sur "Suivant" pour passer à l'étape suivante
            if page.locator('button:has-text("Suivant")').is_visible():
                if stealth:
                    time.sleep(2)
                page.locator('button:has-text("Suivant")').click()
            elif page.locator('button:has-text("Next")').is_visible():
                if stealth:
                    time.sleep(2)
                page.locator('button:has-text("Next")').click()
                
            time.sleep(3)
            
            # Cliquer encore sur "Suivant" si nécessaire (étape de recadrage)
            if page.locator('button:has-text("Suivant")').is_visible():
                if stealth:
                    time.sleep(2)
                page.locator('button:has-text("Suivant")').click()
            elif page.locator('button:has-text("Next")').is_visible():
                if stealth:
                    time.sleep(2)
                page.locator('button:has-text("Next")').click()
                
        except Exception as e:
            print(f"Navigation error: {e}")

        time.sleep(3)

        try:
            # Ajouter la description/caption
            if description:
                if not suppressprint:
                    print("Adding caption...")
                
                # Trouver la zone de texte pour la légende
                caption_area = page.locator('textarea[aria-label*="légende"]')
                if not caption_area.is_visible():
                    caption_area = page.locator('textarea[aria-label*="caption"]')
                if not caption_area.is_visible():
                    caption_area = page.locator('textarea[placeholder*="légende"]')
                if not caption_area.is_visible():
                    caption_area = page.locator('textarea')
                
                caption_area.click()
                if stealth:
                    time.sleep(1)
                caption_area.fill(description)
                
                if not suppressprint:
                    print("Caption added successfully")
                    
        except Exception as e:
            print(f"Error adding caption: {e}")

        # Gestion de la programmation (Instagram Creator Studio nécessaire)
        if schedule and not story_mode:
            try:
                # Note: La programmation directe n'est pas disponible sur instagram.com
                # Il faut utiliser Creator Studio ou l'API
                print("Note: Scheduling not available through web interface")
                print("Video will be posted immediately")
            except Exception as e:
                print(f"Scheduling error: {e}")

        # Attendre que l'upload soit terminé
        if not wait_for_upload_completion(page):
            sys.exit("Upload timeout or failed")

        try:
            # Publier la vidéo
            if not suppressprint:
                print("Publishing video...")
            
            publish_button = page.locator('button:has-text("Partager")')
            if not publish_button.is_visible():
                publish_button = page.locator('button:has-text("Share")')
            if not publish_button.is_visible():
                publish_button = page.locator('button:has-text("Publier")')
            
            if stealth:
                time.sleep(2)
            publish_button.click()
            
            # Attendre la confirmation
            time.sleep(10)
            
            # Vérifier le succès
            success_indicators = [
                'text="Votre publication a été partagée"',
                'text="Your post has been shared"',
                'text="Publication partagée"'
            ]
            
            success = False
            for indicator in success_indicators:
                if page.locator(indicator).is_visible():
                    success = True
                    break
            
            if success or page.url != url:  # URL change indicates success
                if not suppressprint:
                    print("Video uploaded successfully to Instagram!")
            else:
                print("Upload may have failed - please check manually")
                return "Error"
                
        except Exception as e:
            print(f"Error during publishing: {e}")
            return "Error"

        time.sleep(2)
        page.close()
        browser.close()

    return "Completed"

def upload_instagram_story(video: str, accountname: str, 
                          suppressprint: bool = False, headless: bool = True,
                          stealth: bool = False, proxy: dict = None):
    """
    Uploads video as Instagram Story
    """
    return upload_instagram(
        video=video,
        description="",  # Stories don't have captions
        accountname=accountname,
        suppressprint=suppressprint,
        headless=headless,
        stealth=stealth,
        proxy=proxy,
        story_mode=True
    )

# Fonction de test
def test_instagram_upload():
    """Fonction de test pour l'upload Instagram"""
    test_video = "path/to/your/test/video.mp4"
    test_account = "your_instagram_account"
    test_description = "Test upload from automation script! 🚀 #test #automation"
    
    result = upload_instagram(
        video=test_video,
        description=test_description,
        accountname=test_account,
        headless=False,  # Visible pour le débogage
        stealth=True,
        suppressprint=False
    )
    
    print(f"Upload result: {result}")

if __name__ == "__main__":
    # Décommenter pour tester
    # test_instagram_upload()
    pass