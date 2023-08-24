import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import plotly.express as px
import base64
# YouTube API Key
api_key = 'AIzaSyCZZKMNOM5FBE6YDoYS-YwIfqoOH4jsbZU'
youtube = build('youtube', 'v3', developerKey=api_key)

from PIL import Image  # Import PIL library for working with images

# ...

# Streamlit app
st.set_page_config(page_title="YouTube Channel Data Information", page_icon=":bar_chart:")

# Load logo image
logo_path = "https://github.com/M16051997/streamlit-example/blob/master/YouTube-logo.png"
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

    for i in range(len(response['items'])):
        data = dict(Channel_name=response['items'][i]['snippet']['title'],
                    Subscribers=response['items'][i]['statistics']['subscriberCount'],
                    Views=response['items'][i]['statistics']['viewCount'],
                    Total_Videos=response['items'][i]['statistics']['videoCount'])
        Data_all_Channels.append(data)

    return Data_all_Channels

# Download data as Excel
def get_download_link(file_bytes, file_name):
    # Generate a download link
    href = f'<a href="data:application/octet-stream;base64,{base64.b64encode(file_bytes).decode()}" download="{file_name}">Click here to download</a>'
    return href




# Display channel data
if channel_ids:
    channel_data = get_channel_stats(youtube, channel_ids)
    channel_df = pd.DataFrame(channel_data)

    # Create a Markdown table with bold headers
    markdown_table = "| " + " | ".join(channel_df.columns) + " |\n"
    markdown_table += "| " + " | ".join(["---"] * len(channel_df.columns)) + " |\n"
    for index, row in channel_df.iterrows():
        markdown_table += "| " + " | ".join(map(str, row)) + " |\n"

    # Display the Markdown table
    st.markdown(markdown_table)

    # Create a bar plot with different colors for each channel using Plotly
    channel_df['Subscribers'] = channel_df['Subscribers'].apply(int)
    fig = px.bar(channel_df, x='Channel_name', y='Subscribers', title='Subscribers by Channel', color='Channel_name')
    
    # Display the Plotly figure using st.plotly_chart()
    st.plotly_chart(fig)

    # Download data as Excel
    # ...

    # Download data as Excel
    if st.button("Download Data"):
        if channel_ids:
            excel_file_path = "youtube_channel_data.xlsx"
            channel_df.to_excel(excel_file_path, index=False)
            with open(excel_file_path, "rb") as f:
                excel_file_bytes = f.read()
            download_link = get_download_link(excel_file_bytes, "youtube_channel_data.xlsx")
            st.markdown(download_link, unsafe_allow_html=True)
            st.success("Data saved as youtube_channel_data.xlsx")



