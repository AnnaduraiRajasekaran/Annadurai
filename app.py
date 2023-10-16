# Import necessary libraries
import streamlit as st
import pymongo
from mongo_config import MONGODB_URI, DATABASE_NAME
from api_to_mongo import fetch_youtube_data
from migrate_to_sql import migrate_data_to_sql


def main():
    st.title("YouTube Data Harvesting and Warehousing")

    st.sidebar.header("User Input")

    channel_id = st.sidebar.text_input("Enter YouTube Channel ID")

    if st.sidebar.button("Retrieve Channel Details"):
        channel_data = fetch_youtube_data(channel_id)

        # Display channel details
        st.header("Channel Details")
        if "Channel_Name" in channel_data:
            st.write(f"Channel Name: {channel_data['Channel_Name']['Channel_Name']}")
            st.write(f"Channel ID: {channel_data['Channel_Name']['Channel_Id']}")
            st.write(f"Subscription Count: {channel_data['Channel_Name']['Subscription_Count']}")
            st.write(f"Channel Views: {channel_data['Channel_Name']['Channel_Views']}")
            st.write(f"Channel Description: {channel_data['Channel_Name']['Channel_Description']}")

    migrate_channel = st.sidebar.checkbox("Migrate Channel")

    if migrate_channel:
        if st.sidebar.button("Migrate Channel"):
            migrate_data_to_sql()

        # Display a message if a channel is successfully migrated
        st.success("Channel successfully migrated to the data warehouse.")

if __name__ == "__main__":
    main()
