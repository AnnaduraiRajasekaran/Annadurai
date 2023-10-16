import pymongo
from googleapiclient.discovery import build
from mongo_config import MONGODB_URI,API_KEY

def save_data_to_mongodb(data):
        client = pymongo.MongoClient(MONGODB_URI)
        db = client.youtube
        channel_collection = db.Channel
        channel_collection.insert_one(data["Channel_Name"])

        #Insert playlist data
        playlist_collection = db.Playlist
        playlist_collection.insert_one(data["Channel_Name"])
        playlist_collection.update_one(
            {"_id": data["Channel_Name"]["_id"]},
            {"$set": {"Playlist_Id": data["Channel_Name"]["Playlist_Id"]}}
        )

        # Insert video data
        for video_id, video_data in data.items():
            if video_id != "Channel_Name":
                video_collection = db.Video
                video_collection.insert_one(video_data)
    
def fetch_youtube_data(channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    client = pymongo.MongoClient(MONGODB_URI)
    db = client.youtube

    

    def get_all_playlists(channel_id):
        playlists = []

        next_page_token = None

        while True:
            playlist_response = youtube.playlists().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            if 'items' in playlist_response:
                playlists.extend(playlist_response['items'])

            next_page_token = playlist_response.get('nextPageToken')

            if not next_page_token:
                break

        return playlists

    data = {
        "Channel_Name": {
            "Channel_Name": "",
            "Channel_Id": channel_id,
            "Subscription_Count": 0,
            "Channel_Views": 0,
            "Channel_Description": "",
            "Playlist_Id": {}
        }
    }

    channel_response = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    ).execute()

    if 'items' in channel_response:
        channel_info = channel_response['items'][0]
        data["Channel_Name"]["Channel_Name"] = channel_info['snippet']['title']
        data["Channel_Name"]["Subscription_Count"] = int(channel_info['statistics']['subscriberCount'])
        data["Channel_Name"]["Channel_Views"] = int(channel_info['statistics']['viewCount'])
        data["Channel_Name"]["Channel_Description"] = channel_info['snippet']['description']

    playlists_data = get_all_playlists(channel_id)
    

    if playlists_data:
        playlists = []

        for playlist_data in playlists_data:
            playlist_info = {
                "Playlist_Id": playlist_data['id'],
                "Playlist_Title": playlist_data['snippet']['title']
            }
            playlists.append(playlist_info)

        # print(playlists)

        channel_collection = db.Channel
        channel_collection.update_one(
            {"Channel_Id": channel_id},
            {"$set": {"Playlists": playlists}}
        )

        for playlist_info in playlists:
            playlist_id = playlist_info["Playlist_Id"]
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50
            ).execute()

            if 'items' in playlist_response:
                for item in playlist_response['items']:
                    thumbnail_data = item['snippet']['thumbnails'].get('default')
                    thumbnail_url = thumbnail_data['url'] if thumbnail_data else None

                    video_data = {
                        "Video_Id": item['snippet']['resourceId']['videoId'],
                        "Video_Name": item['snippet']['title'],
                        "Video_Description": item['snippet']['description'],
                        "Tags": [],
                        "PublishedAt": item['snippet']['publishedAt'],
                        "View_Count": 0,
                        "Like_Count": 0,
                        "Dislike_Count": 0,
                        "Favorite_Count": 0,
                        "Comment_Count": 0,
                        "Duration": "",
                        "Thumbnail": thumbnail_url,
                        "Caption_Status": "Not Available",
                        "Comments": {},
                        "Channel_Id":channel_id,
                        "Playlist_Id": playlist_id
                    }

                    # Retrieve video statistics
                    video_response = youtube.videos().list(
                        part='statistics,contentDetails',
                        id=video_data["Video_Id"]
                    ).execute()

                    if 'items' in video_response:
                        video_info = video_response['items'][0]
                        video_data["View_Count"] = int(video_info['statistics']['viewCount'])
                        video_data["Like_Count"] = int(video_info['statistics']['likeCount'])
                        video_data["Dislike_Count"] = int(video_info['statistics'].get('dislikeCount',-1))
                        video_data["Favorite_Count"] = int(video_info['statistics']['favoriteCount'])
                        video_data["Comment_Count"] = int(video_info['statistics']['commentCount'])
                        video_data["Duration"] = video_info['contentDetails']['duration']

    #                 # Retrieve video captions
    #                 captions_response = youtube.captions().list(
    #                     part='snippet',
    #                     videoId=video_data["Video_Id"]
    #                 ).execute()

    #                 if 'items' in captions_response:
    #                     video_data["Caption_Status"] = "Available"

    #                 # Retrieve video comments
    #                 comments_response = youtube.commentThreads().list(
    #                     part='snippet',
    #                     videoId=video_data["Video_Id"],
    #                     textFormat='plainText',
    #                     maxResults=50  # Adjust as needed
    #                 ).execute()

    #                 if 'items' in comments_response:
    #                     video_data["Comments"] = {}
    #                     for comment_thread in comments_response['items']:
    #                         comment = comment_thread['snippet']['topLevelComment']['snippet']
    #                         comment_data = {
    #                             "Comment_Id": comment_thread['id'],
    #                             "Comment_Text": comment['textDisplay'],
    #                             "Comment_Author": comment['authorDisplayName'],
    #                             "Comment_PublishedAt": comment['publishedAt']
    #                         }
                        #video_data["Comments"][comment_thread['id']] = comment_data

                        data[item['snippet']['resourceId']['videoId']] = video_data



    save_data_to_mongodb(data)

    client.close()

    return data
