from playwright.sync_api import sync_playwright
import logging
import time
import re
import os
from urllib.parse import unquote
import random

OUTPUT_FILE = "download/links.txt"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("download/tiktok_scraper.log"), logging.StreamHandler()]
)
logger = logging.getLogger("TikTokScraper")

def extract_video_links(page_content):
    """Extraction des liens avec décodage URL"""
    decoded_content = unquote(page_content)
    pattern = re.compile(
        r'(https?://(www\.)?tiktok\.com/@[A-Za-z0-9_.-]+/video/\d+)(?:\\?/|\?|")'
    )
    return {match[0].replace('\\', '') for match in pattern.findall(decoded_content)}

def scrape_hashtag(hashtag, max_links=10):
    """Scraping avec gestion avancée du scroll"""
    results = set()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(100,125)}.0.0.0 Safari/537.36'
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='fr-FR',
            timezone_id='Europe/Paris'
        )
        
        page = context.new_page()
        
        try:
            page.goto(f'https://www.tiktok.com/tag/{hashtag}', timeout=60000)
            
            # Système de scroll adaptatif
            previous_count = 0
            retry_count = 0
            
            while len(results) < max_links and retry_count < 5:
                # Scroll progressif
                for _ in range(3):
                    page.mouse.wheel(0, random.randint(300, 700))
                    time.sleep(random.uniform(0.5, 1.2))
                
                # Attente dynamique
                page.wait_for_timeout(random.randint(1000, 3000))
                
                # Extraction des liens
                content = page.content()
                new_links = extract_video_links(content)
                current_count = len(results)
                results.update(new_links)
                
                # Vérification du progrès
                if len(results) > current_count:
                    logger.info(f"Hashtag #{hashtag} - Liens trouvés : {len(results)}/{max_links}")
                    retry_count = 0
                else:
                    retry_count += 1
                    # Contournement anti-bot
                    if retry_count % 2 == 0:
                        page.keyboard.press('PageDown')
                        time.sleep(random.uniform(1, 2))
                
                if len(results) >= max_links:
                    break

        except Exception as e:
            logger.error(f"Erreur: {str(e)}")
        finally:
            browser.close()
    
    return list(results)[:max_links]

def save_links(links, filename):
    """Enregistrement des liens avec vérification de format"""
    valid_links = []
    pattern = re.compile(r'^https?://(www\.)?tiktok\.com/@[^/]+/video/\d+$')
    
    for link in links:
        if pattern.match(link):
            valid_links.append(link)
        else:
            logger.warning(f"Lien invalide filtré : {link}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(valid_links))
    
    logger.info(f"{len(valid_links)} liens valides enregistrés dans {filename}")
    
    

def Scrappe_Main(HASHTAGS : list[str] , NUM_LINK : int = 3 , FILE_path : str = "download/links.txt"):
    """Fonction principale de scraping"""
    # Scraping
    all_links = []
    for hashtag in HASHTAGS:
        logger.info(f"Début du scraping pour #{hashtag}")
        links = scrape_hashtag(hashtag, NUM_LINK)
        all_links.extend(links)
        logger.info(f"Terminé pour #{hashtag} - {len(links)} liens trouvés")
    
    # Enregistrement final
    save_links(all_links, FILE_path)
    logger.info("Opération terminée avec succès!")
    print(f"\nLes liens ont été enregistrés dans : {os.path.abspath(OUTPUT_FILE)}")
    

if __name__ == "__main__":
    # Configuration
    HASHTAGS = ["valorant", "zelda"]
    MAX_LINKS_PER_HASHTAG = 10
    OUTPUT_FILE = "download/links.txt"
    
    # Création du dossier
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Scraping
    all_links = []
    for hashtag in HASHTAGS:
        logger.info(f"Début du scraping pour #{hashtag}")
        links = scrape_hashtag(hashtag, MAX_LINKS_PER_HASHTAG)
        all_links.extend(links)
        logger.info(f"Terminé pour #{hashtag} - {len(links)} liens trouvés")
    
    # Enregistrement final
    save_links(all_links, OUTPUT_FILE)
    logger.info("Opération terminée avec succès!")
    print(f"\nLes liens ont été enregistrés dans : {os.path.abspath(OUTPUT_FILE)}")