import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import plotly.express as px
import base64
# YouTube API Key
api_key = 'AIzaSyBKjbT5XWKMZprBSgTZkMyk0-wtSVO7U-Q'
youtube = build('youtube', 'v3', developerKey=api_key)

from PIL import Image  # Import PIL library for working with images

# ...

# Streamlit app
st.set_page_config(page_title="YouTube Channel Analytics", page_icon=":bar_chart:")

# Load logo image
logo_path = r"F:\Streamlit\YouTube-logo.png"
with open(logo_path, "rb") as logo_file:
    logo_image = base64.b64encode(logo_file.read()).decode()

# Display the logo on the main page using HTML and CSS
st.markdown(
    f"""
    <style>
        .logo-container {{
            display: flex;
            align-items: center;
            padding-left: 20px;
        }}
        .logo-img {{
            width: 250px;
            margin-right: 50px;
        }}
    </style>
    <div class="logo-container">
        <img class="logo-img" src="data:image/png;base64,{logo_image}" alt="YouTube Logo">
                           <h1>YouTube Channel Information</h1>
    </div>
    """,
    unsafe_allow_html=True
)



# Input tabs for channel IDs
st.sidebar.title("Input Channels")
channel_ids = st.sidebar.text_area("Enter Channel IDs (one per line)", "").splitlines()

# Extract data function
def get_channel_stats(youtube, channel_ids):

    Data_all_Channels = []

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id= ','.join(channel_ids))
    response = request.execute()

    for i in range(len(response['items'])):         #Loop the Items
        data = dict(Channel_name = response['items'][i]['snippet']['title'],
                    Subscribers = response['items'][i]['statistics']['subscriberCount'],
                    Views = response['items'][i]['statistics']['viewCount'],
                    Total_Videos = response['items'][i]['statistics']['videoCount'],
                    Playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
        Data_all_Channels.append(data)

    return Data_all_Channels

# Taking Videos Id's

# Taking Videos Id's

def get_video_Ids(youtube, id):
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId = id,
        maxResults = 50  ) # For taking More Data
        # id= ','.join(channel_ids)
    response = request.execute()

    video_ids = []

    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
    next_page_token = response.get('nextPageToken')
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages  = False
        else:
            request = youtube.playlistItems().list(
                        part="contentDetails",
                        playlistId = id,
                        maxResults = 50,            # For taking More Data
                        pageToken = next_page_token ) 
                        
            response = request.execute()

            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            next_page_token = response.get('nextPageToken')
    return video_ids


# Get All Vedios Iterate Through all by giving 50 Videos at a time

def get_video_details(youtube, video_Ids):

    all_video = []

    for i in range(0, len(video_Ids), 50):
        request = youtube.videos().list(
                part = 'snippet,statistics',
                id = ','.join(video_Ids[i:i+50]))  # First it will take 0 + 50 = 50 than 50 + 50 = 100
        response = request.execute()

        for video in response['items']:
                video_stats = dict( Date_Published = video['snippet']['publishedAt'],
                                        Title = video['snippet']['title'],
                                        Tags = video['snippet'].get('tags', 0),
                                        channel = video['snippet']['channelTitle'],
                                        Comments = video['statistics'].get('commentCount', 0),
                                        viewCount = video['statistics']['viewCount'],
                                        likeCount = video['statistics'].get('likeCount', 0),
                                        favoriteCount = video['statistics']['favoriteCount']
                                        )
                all_video.append(video_stats)
    
    return all_video

# Download data as Excel
def get_download_link(file_bytes, file_name):
    # Generate a download link
    href = f'<a href="data:application/octet-stream;base64,{base64.b64encode(file_bytes).decode()}" download="{file_name}">Click here to download</a>'
    return href




# Display channel data
if channel_ids:
    channel_data = get_channel_stats(youtube, channel_ids)
    channel_df = pd.DataFrame(channel_data)

    channel_dt = channel_df[['Channel_name','Subscribers', 'Views', 'Total_Videos']]
    # Create a Markdown table with bold headers
    markdown_table = "| " + " | ".join(channel_dt.columns) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(channel_dt.columns)) + " |\n"
    for index, row in channel_dt.iterrows():
        markdown_table += "| " + " | ".join(map(str, row)) + " |\n"
    
    st.header("Channel Information:--")
    # Display the Markdown table
    st.markdown(markdown_table)
    
    ds = []

    for i in channel_df['Playlist_id']:
        ds.append(i)
        
    
    # Than Extract the Video ID's By using Playlist ID's in the channel_df Dataframe
    data = []
    for ids in ds:
        vide = get_video_Ids(youtube, ids)  # 
        data.append(vide)
    
    
    Dataset = []

    for ta in data:
        dddd = get_video_details(youtube, ta)
        Dataset.extend(dddd)

    # Dataset = get_video_details(youtube, data)
    st.header("Channel/Channels Data:--")
    Dataset1 = pd.DataFrame(Dataset)
    Dataset1['Comments'] = Dataset1['Comments'].astype('int')
    Dataset1['viewCount'] = Dataset1['viewCount'].astype('int')
    Dataset1['likeCount'] = Dataset1['likeCount'].astype('int')
    Dataset1['Date'] = pd.to_datetime(Dataset1['Date_Published'])

    Dataset1['Tags'] = Dataset1['Tags'].astype('str')
    Dataset1['Enagement'] = Dataset1['Comments'] + Dataset1['viewCount']  + Dataset1['likeCount']


    # Add a date filter
    from datetime import datetime
    # Add a date filter
    st.sidebar.header("Date Filter")
    selected_date_range = st.sidebar.date_input("Select a date range", (Dataset1['Date'].min().date(), Dataset1['Date'].max().date()))

    # Convert selected date range to UTC
    start_date = pd.Timestamp(selected_date_range[0]).tz_localize('UTC')
    end_date = pd.Timestamp(selected_date_range[1]).tz_localize('UTC')

    # Filter Dataset1 based on the selected date range
    filtered_dataset = Dataset1[
        (Dataset1['Date'] >= start_date) & (Dataset1['Date'] <= end_date)
    ]

    # Rest of your code...

    st.write(filtered_dataset)
    

    from datetime import datetime   

    

    # Create a bar plot with different colors for each channel using Plotly
    fig = px.bar(filtered_dataset, x='channel', y='Enagement', title='Enagement by Channel', color='channel')
    
    # Display the Plotly figure using st.plotly_chart()
    st.plotly_chart(fig)

    # Enagagement Trend
    fig1 = px.line(filtered_dataset, x='Date', y='Enagement', color='channel', title='Engagement Trend by Channel')
    # Display the Plotly figure using st.plotly_chart()
    st.plotly_chart(fig1)

    # Comments Trend
    fig2 = px.line(filtered_dataset, x='Date', y='Comments', color='channel', title='Comments Trend by Channel')
    # Display the Plotly figure using st.plotly_chart()
    st.plotly_chart(fig2)

    # Like Trend
    fig3 = px.line(filtered_dataset, x='Date', y='likeCount', color='channel', title='Likes Trend by Channel')
    # Display the Plotly figure using st.plotly_chart()
    st.plotly_chart(fig3)


    Top20_videos = filtered_dataset.sort_values(by='Enagement', ascending=False).head(20)
    # Create a bar plot for the top 10 videos by engagement
    fig4 = px.bar(Top20_videos, x='Enagement', y='Title', color='channel',
                title='Top 20 Videos by Channel')
    # Customize the layout if needed
    fig4.update_layout(xaxis_title='Engagement', yaxis_title='Video Title')
    # Show the plot
    st.plotly_chart(fig4)



    # Download data as Excel
    # ...

    # Download data as Excel
    if st.button("Download Data"):
        if channel_ids:
            excel_file_path = "youtube_channel_data.xlsx"
            filtered_dataset['Date'] = filtered_dataset['Date'].astype('str')
            filtered_dataset.to_excel(excel_file_path, index=False)
            with open(excel_file_path, "rb") as f:
                excel_file_bytes = f.read()
            download_link = get_download_link(excel_file_bytes, "youtube_channel_data.xlsx")
            st.markdown(download_link, unsafe_allow_html=True)
            st.success("Data saved as youtube_channel_data.xlsx")



