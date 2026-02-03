import datetime
import os
import time
from instagram_function import upload_instagram, upload_instagram_story

# Configuration de la vidéo
video_path = "C:/Users/romai/Videos/upload_shorts_tiktok/upload/Worst dad jokes of all time 😂💀 sound.mp4"
video_title = 'best dad jokes'

# Paramètres de publication
publish_instagram_post = True
publish_instagram_story = False

# Choix du compte Instagram
instagram_accountname = 'your_instagram_account'  # Remplacez par votre nom de compte

# Description Instagram (peut inclure hashtags)
instagram_description = f"""🎬 {video_title}

Like and follow for more content! 

#jokes #funny #comedy #humor #viral #entertainment #fyp #reels #explore"""

# Configuration temporelle
marge = 0  # Instagram ne supporte pas la programmation native
current_time = datetime.datetime.now()
print("Current time:", current_time)

def upload_to_instagram():
    """Lance l'upload vers Instagram"""
    
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found at {video_path}")
        return
    
    try:
        if publish_instagram_post:
            print("Début de l'upload Instagram Post")
            result = upload_instagram(
                video=video_path,
                description=instagram_description,
                accountname=instagram_accountname,
                stealth=True,
                headless=False,  # Visible pour pouvoir intervenir si nécessaire
                suppressprint=False
            )
            
            if result == "Completed":
                print("✅ Instagram Post uploaded successfully!")
            else:
                print("❌ Instagram Post upload failed!")
        
        if publish_instagram_story:
            print("Début de l'upload Instagram Story")
            result = upload_instagram_story(
                video=video_path,
                accountname=instagram_accountname,
                stealth=True,
                headless=False,
                suppressprint=False
            )
            
            if result == "Completed":
                print("✅ Instagram Story uploaded successfully!")
            else:
                print("❌ Instagram Story upload failed!")
                
    except Exception as e:
        print(f"Error during Instagram upload: {str(e)}")
    
    print("Instagram upload process completed")

if __name__ == "__main__":
    upload_to_instagram()