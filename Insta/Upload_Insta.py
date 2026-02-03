import datetime
import os
import time
from pathlib import Path
from instagram_function import upload_instagram, upload_instagram_story

def upload_videos_from_folder_instagram(folder_path: str, instagram_accountname: str,
                                       default_hashtags: list = None, 
                                       interval_hours: float = 1.0,
                                       start_time: datetime.datetime = None,
                                       story_mode: bool = False,
                                       stealth: bool = True,
                                       headless: bool = False):
    """
    Upload multiple videos to Instagram from a folder
    
    Args:
        folder_path (str): Path to folder containing videos
        instagram_accountname (str): Instagram account name
        default_hashtags (list): List of hashtags to add to each post
        interval_hours (float): Hours between each upload (for manual scheduling)
        start_time (datetime): When to start uploading
        story_mode (bool): Upload as stories instead of posts
        stealth (bool): Add delays between actions
        headless (bool): Run browser in headless mode
    """
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder {folder_path} does not exist")
        return
    
    # Find all video files
    video_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.mkv']
    video_files = []
    
    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(file)
    
    if not video_files:
        print("No video files found in the folder")
        return
    
    print(f"Found {len(video_files)} videos to upload")
    
    # Prepare hashtags
    hashtag_string = ""
    if default_hashtags:
        hashtag_string = " " + " ".join([f"#{tag.strip('#')}" for tag in default_hashtags])
    
    # Set start time
    if start_time is None:
        start_time = datetime.datetime.now()
    
    current_time = start_time
    successful_uploads = 0
    failed_uploads = []
    
    for i, video_file in enumerate(video_files):
        video_path = os.path.join(folder_path, video_file)
        video_name = os.path.splitext(video_file)[0]
        
        # Create description
        if not story_mode:
            description = f"🎬 {video_name}\n\nLike and follow for more content!{hashtag_string}\n\n#fyp #viral #explore #reels"
        else:
            description = ""  # Stories don't have captions
        
        print(f"\n--- Uploading video {i+1}/{len(video_files)}: {video_file} ---")
        print(f"Scheduled for: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # For now, Instagram doesn't support native scheduling, so we upload immediately
            # In the future, you could add a delay mechanism here
            
            if story_mode:
                result = upload_instagram_story(
                    video=video_path,
                    accountname=instagram_accountname,
                    stealth=stealth,
                    headless=headless,
                    suppressprint=False
                )
            else:
                result = upload_instagram(
                    video=video_path,
                    description=description,
                    accountname=instagram_accountname,
                    stealth=stealth,
                    headless=headless,
                    suppressprint=False
                )
            
            if result == "Completed":
                successful_uploads += 1
                print(f"✅ Successfully uploaded: {video_file}")
            else:
                failed_uploads.append(video_file)
                print(f"❌ Failed to upload: {video_file}")
            
            # Add delay between uploads to avoid being flagged
            if i < len(video_files) - 1:  # Don't wait after the last video
                wait_time = max(60, interval_hours * 3600)  # At least 1 minute between uploads
                print(f"Waiting {wait_time/60:.1f} minutes before next upload...")
                time.sleep(wait_time)
            
        except Exception as e:
            failed_uploads.append(video_file)
            print(f"❌ Error uploading {video_file}: {str(e)}")
        
        current_time += datetime.timedelta(hours=interval_hours)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"UPLOAD SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Successful uploads: {successful_uploads}/{len(video_files)}")
    print(f"❌ Failed uploads: {len(failed_uploads)}")
    
    if failed_uploads:
        print("\nFailed videos:")
        for video in failed_uploads:
            print(f"  - {video}")
    
    return successful_uploads, failed_uploads

def create_instagram_post_description(video_title: str, hashtags: list = None, 
                                    custom_text: str = None) -> str:
    """
    Creates a formatted Instagram post description
    
    Args:
        video_title (str): Title of the video
        hashtags (list): List of hashtags
        custom_text (str): Custom text to add
    
    Returns:
        str: Formatted description
    """
    
    description_parts = []
    
    # Add emoji and title
    description_parts.append(f"🎬 {video_title}")
    description_parts.append("")
    
    # Add custom text if provided
    if custom_text:
        description_parts.append(custom_text)
        description_parts.append("")
    
    # Add call to action
    description_parts.append("Like and follow for more content! 💫")
    description_parts.append("")
    
    # Add hashtags
    if hashtags:
        hashtag_line = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
        description_parts.append(hashtag_line)
        description_parts.append("")
    
    # Add default hashtags
    default_hashtags = "#fyp #viral #explore #reels #entertainment"
    description_parts.append(default_hashtags)
    
    return "\n".join(description_parts)

# Presets for different types of content
INSTAGRAM_PRESETS = {
    "parkour": {
        "hashtags": ["parkour", "freerun", "urbanbeastmode", "sports", "extreme"],
        "custom_text": "Epic parkour moves! 🏃‍♂️💨"
    },
    "gaming": {
        "hashtags": ["gaming", "valorant", "gamer", "esports", "clutch"],
        "custom_text": "Gaming highlights! 🎮🔥"
    },
    "comedy": {
        "hashtags": ["comedy", "funny", "jokes", "humor", "laugh"],
        "custom_text": "Hope this made you laugh! 😂"
    },
    "motivation": {
        "hashtags": ["motivation", "inspiration", "mindset", "success", "growth"],
        "custom_text": "Daily motivation boost! 💪✨"
    },
    "psychology": {
        "hashtags": ["psychology", "facts", "mind", "brain", "knowledge"],
        "custom_text": "Interesting psychology facts! 🧠💡"
    }
}

def upload_with_preset(video_path: str, accountname: str, preset_name: str, 
                      custom_title: str = None, story_mode: bool = False):
    """
    Upload a single video with a predefined preset
    
    Args:
        video_path (str): Path to the video file
        accountname (str): Instagram account name
        preset_name (str): Name of the preset to use
        custom_title (str): Custom title (uses filename if not provided)
        story_mode (bool): Upload as story
    """
    
    if preset_name not in INSTAGRAM_PRESETS:
        print(f"Unknown preset: {preset_name}")
        print(f"Available presets: {', '.join(INSTAGRAM_PRESETS.keys())}")
        return
    
    preset = INSTAGRAM_PRESETS[preset_name]
    
    # Get video title
    if custom_title:
        title = custom_title
    else:
        title = os.path.splitext(os.path.basename(video_path))[0]
    
    # Create description (only for posts, not stories)
    if not story_mode:
        description = create_instagram_post_description(
            video_title=title,
            hashtags=preset["hashtags"],
            custom_text=preset["custom_text"]
        )
    else:
        description = ""
    
    # Upload
    if story_mode:
        result = upload_instagram_story(
            video=video_path,
            accountname=accountname,
            stealth=True,
            headless=False,
            suppressprint=False
        )
    else:
        result = upload_instagram(
            video=video_path,
            description=description,
            accountname=accountname,
            stealth=True,
            headless=False,
            suppressprint=False
        )
    
    return result

# Example usage
if __name__ == "__main__":
    # Example 1: Upload a single video with comedy preset
    upload_with_preset(
        video_path="path/to/your/video.mp4",
        accountname="your_instagram_account",
        preset_name="comedy",
        custom_title="Best Dad Jokes Ever"
    )
    
    # Example 2: Upload multiple videos from folder
    # upload_videos_from_folder_instagram(
    #     folder_path="path/to/video/folder",
    #     instagram_accountname="your_instagram_account",
    #     default_hashtags=["funny", "comedy", "viral"],
    #     interval_hours=2.0,
    #     story_mode=False
    # )
    
    pass