import pymongo
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mongo_config import MONGODB_URI, DATABASE_NAME



Base = declarative_base()

class Channel(Base):
    __tablename__ = "Channel"
    channel_id = Column(String(255), primary_key=True)
    channel_name = Column(String(255))
    channel_type = Column(String(255))
    channel_views = Column(Integer)
    channel_description = Column(Text)
    channel_status = Column(String(255))

class Playlist(Base):
    __tablename__ = "Playlist"
    playlist_id = Column(String(255), primary_key=True)
    channel_id = Column(String(255), sqlalchemy.ForeignKey('Channel.channel_id'))
    playlist_name = Column(String(255))

class Comment(Base):
    __tablename__ = "Comment"
    comment_id = Column(String(255), primary_key=True)
    video_id = Column(String(255), sqlalchemy.ForeignKey('Video.video_id'))
    comment_text = Column(Text)
    comment_author = Column(String(255))
    comment_published_date = Column(DateTime)

class Video(Base):
    __tablename__ = "Video"
    video_id = Column(String(255), primary_key=True)
    playlist_id = Column(String(255), sqlalchemy.ForeignKey('Playlist.playlist_id'))
    video_name = Column(String(255))
    video_description = Column(Text)
    published_date = Column(DateTime)
    view_count = Column(Integer)
    like_count = Column(Integer)
    dislike_count = Column(Integer)
    favorite_count = Column(Integer)
    comment_count = Column(Integer)
    duration = Column(Integer)
    thumbnail = Column(String(255))
    caption_status = Column(String(255))

def migrate_data_to_sql():
    # Connect to MongoDB
    mongo_client = pymongo.MongoClient(MONGODB_URI)
    mongo_db = mongo_client[DATABASE_NAME]
    channel_collection = mongo_db["Channel"]
    video_collection=mongo_db["Video"]
    playlist_collection=mongo_db["Playlist"]

    # Connect to the SQL database (MySQL in this example)
    sql_engine = create_engine("mysql+mysqlconnector://root:@localhost/youtube")

    # Create the SQL tables if they don't exist
    Base.metadata.create_all(sql_engine)

    # Create a SQLAlchemy session
    Session = sessionmaker(bind=sql_engine)
    session = Session()

    # Retrieve data from MongoDB and insert it into the SQL tables
    channel_data = list(channel_collection.find())
    #print(type(channel_data))
    #print(channel_data)
    Video_data=list(video_collection.find())
    playlist_data=list(playlist_collection.find())
    print(playlist_data)
    for entry in channel_data:
        channel_data = Channel(
            channel_id=entry['Channel_Id'],
            channel_name=entry['Channel_Name'],
            channel_type='Public',
            channel_views=entry['Channel_Views'],
            channel_description=entry['Channel_Description'],
            channel_status='Active'
        )

        session.add(channel_data)

        break

        #Example for the Playlist table:
    for playlist_info in playlist_data:
        playlist_data = Playlist(
            playlist_id=playlist_info['Playlist_Id'],
            channel_id=entry['Channel_Id'],
            playlist_name=playlist_info['Playlist_Title']
        )
        session.add(playlist_data)

    #     # Example for the Video table:
    # for video_info in video_data:
    #         video_data = Video(
    #             video_id=video_info['Video_Id'],
    #             playlist_id=video_info['Playlist_Id'],
    #             video_name=video_info['Video_Name'],
    #             video_description=video_info['Video_Description'],
    #             published_date=video_info['PublishedAt'],
    #             view_count=video_info['View_Count'],
    #             like_count=video_info['Like_Count'],
    #             dislike_count=video_info['Dislike_Count'],
    #             favorite_count=video_info['Favorite_Count'],
    #             comment_count=video_info['Comment_Count'],
    #             duration=video_info['Duration'],
    #             thumbnail=video_info['Thumbnail'],
    #             caption_status=video_info['Caption_Status']
    #         )
    #         session.add(video_data)

    #             # Example for the Comment table:
    #         for comment_id, comment_info in video_info['Comments'].items():
    #             comment_data = Comment(
    #                 comment_id=comment_info['Comment_Id'],
    #                 video_id=video_info['Video_Id'],
    #                 comment_text=comment_info['Comment_Text'],
    #                 comment_author=comment_info['Comment_Author'],
    #                 comment_published_date=comment_info['Comment_PublishedAt']
    #             )
    #             session.add(comment_data)

    session.commit()


    session.close()
    mongo_client.close()

if __name__ == "__main__":
    migrate_data_to_sql()