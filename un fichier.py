import datetime
from Tiktok.function import upload_tiktok
from Youtube.YT_upload_API import upload_youtube
from Insta.Upload_Insta import *

# All configurations
video_path : str = "C:/Users/romai/Videos/upload_shorts_tiktok/upload/Worst dad jokes of all time 😂💀 sound.mp4"
# video_path : str = "download/video/6938010153795063046.mp4"
# video_path : str = "C:/Users/Administrateur/Videos/bot check.mp4"
# video_path : str = ""


video_title : str = 'best dad jokes'

# parametre important à changer pour chaque vidéo
tiktok : bool = True
youtube : bool = False
insta : bool = False


# choix du compte sur lequel on veut poster
insta_accountname = ""

# tiktok_accountname = 'urban_beast_mode'
tiktok_accountname = 'jokemeup'
# tiktok_accountname = 'psychologie_astuce_'
# tiktok_accountname = 'crocsrouges'

# tiktok_hashtags = ['#parkour ', '#freerun ', '#urbanbeastmode ']
# tiktok_hashtags = ['#gaming ', '#valorant ', '#Valorant '] # pour les vidéos de gaming
# tiktok_hashtags = ['#psychologie ', '#astuce ', '#motivation ']
tiktok_hashtags = ["jokes", "funnytok"] # pour les vidéos d'humour

# YouTube configurations
video_description : str = "Description de la vidéo"
video_tags : list = ["parkour", "sports" , "freerunning"]
video_category_id : int = "20"  # Category 'Gaming'

marge : int = 3 # marge de temps en plus pour que la vidéo puisse se publier sur youtube sans problème

sound_name = "juno"


# Calculate the scheduled time in UTC
current_time_utc : datetime = datetime.datetime.now(datetime.timezone.utc)
print("Current time:", current_time_utc)

# Ensure scheduled time is at least 15 minutes ahead and minutes are multiples of 5
earliest_time = current_time_utc + datetime.timedelta(minutes=15)
minutes = earliest_time.minute
remainder = minutes % 5
add_minutes = 5 - remainder if remainder != 0 else 0

scheduled_time_utc = earliest_time + datetime.timedelta(hours= marge, minutes=add_minutes)
scheduled_time_utc = scheduled_time_utc.replace(second=0, microsecond=0)


# Convert scheduled time to local time for TikTok parameters
day_of_month = scheduled_time_utc.day
day_of_month += 1
schedule_time_format = scheduled_time_utc.strftime("%H:%M")

print("Formatted schedule time for TikTok:", schedule_time_format)
print("Day of the month for TikTok:", day_of_month)

def upload_video():
    if tiktok:
        print("Début de Tiktok")
        upload_tiktok(
            video=video_path,
            description=video_title,
            accountname=tiktok_accountname,
            hashtags=tiktok_hashtags,
            schedule=schedule_time_format,
            day=day_of_month,
            sound_name= sound_name ,
            sound_aud_vol= "background",
            stealth= True,
            headless= False
        )
        print("Fin de Tiktok")
        
    if youtube:
        # Upload to YouTube
        print("Début de Youtube")
        upload_youtube(
            file_path=video_path,
            title=video_title,
            description=video_description,
            tags=video_tags,
            category_id=video_category_id,
            scheduled_time=scheduled_time_utc
        )
        print("Fin de Youtube")
    if insta:
        # Upload on Instagram
        print("Début de Insta")
        upload_instagram(
            video= video_path,
            description= video_title,
            accountname= insta_accountname,
            schedule= schedule_time_format,
            day= day_of_month,            
        )
        print("Fin de Insta")

    print("Process completed")
    
upload_video()