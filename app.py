import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen, Request
from newspaper import Article
import io
import nltk
import logging

# Download necessary NLTK data
nltk.download('punkt')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Streamlit configuration
st.set_page_config(page_title="InNews - Modern News Portal", layout="wide", page_icon="📰")

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"  # Default to Home page

# Functions to fetch news
def fetch_news_search_topic(topic):
    site = f'https://news.google.com/rss/search?q={topic}'
    return fetch_rss_feed(site)

def fetch_top_news():
    site = 'https://news.google.com/rss'
    return fetch_rss_feed(site)

def fetch_category_news(topic):
    site = f'https://news.google.com/news/rss/headlines/section/topic/{topic}'
    return fetch_rss_feed(site)

def fetch_rss_feed(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url, headers=headers)
        op = urlopen(req)
        rd = op.read()
        op.close()
        sp_page = soup(rd, 'xml')
        news_list = sp_page.find_all('item')
        return news_list
    except Exception as e:
        st.error(f"Failed to fetch RSS feed: {e}")
        return []

# Function to fetch images
def fetch_image_from_rss(news_item):
    media_content = news_item.find('media:content')
    if media_content and 'url' in media_content.attrs:
        return media_content['url']
    enclosure = news_item.find('enclosure')
    if enclosure and 'url' in enclosure.attrs:
        return enclosure['url']
    image_tag = news_item.find('image')
    if image_tag and image_tag.text:
        return image_tag.text
    return None

def fetch_image_from_newspaper(article_url):
    try:
        news_data = Article(article_url)
        news_data.download()
        news_data.parse()
        return news_data.top_image
    except Exception as e:
        logging.error(f"Error fetching image from newspaper: {e}")
        return None

# Function to display news in grid format with styling
def display_news_grid(news_list):
    cols = st.columns(3)  # Create a 3-column grid
    for i, news in enumerate(news_list):
        col = cols[i % 3]  # Distribute news across columns
        with col:
            # Add custom CSS to style the columns (margin, padding, border)
            st.markdown(
                f"""
                <div style="border: 2px solid #ccc; padding: 10px; margin: 10px; border-radius: 8px;">
                    <h3>{news.title.text}</h3>
                    <p><strong>Source:</strong> {news.source.text if news.source else 'Unknown'}</p>
                    <p><strong>Published:</strong> {news.pubDate.text if news.pubDate else 'Unknown'}</p>
                    <a href="{news.link.text}" target="_blank">Read Article</a>
                </div>
                """,
                unsafe_allow_html=True
            )

            # # Attempt to fetch and display image
            # image_url = fetch_image_from_rss(news)
            # if not image_url:
            #     image_url = fetch_image_from_newspaper(news.link.text)
            # if image_url:
            #     try:
            #         u = urlopen(image_url)
            #         raw_data = u.read()
            #         image = Image.open(io.BytesIO(raw_data))
            #         st.image(image, use_column_width=True)
            #     except Exception as e:
            #         logging.error(f"Error loading image: {e}")

# Navigation buttons horizontally aligned
def render_navigation():
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button('🏠 Home'):
            st.session_state.page = 'Home'
    with col2:
        if st.button('📂 Categories'):
            st.session_state.page = 'Categories'
    with col3:
        if st.button('🔍 Search'):
            st.session_state.page = 'Search'

# Render the appropriate page based on session state
def render_page():
    if st.session_state.page == "Home":
        st.title("Trending🔥 News")
        news_list = fetch_top_news()
        if news_list:
            display_news_grid(news_list[:9])  # Display in grid format
        else:
            st.info("No news available at the moment.")
    
    elif st.session_state.page == "Categories":
        st.title("Choose a Category 📂")
        categories = ['WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        chosen_category = st.selectbox("Select a category", options=categories)
        if chosen_category:
            st.subheader(f"Showing news for **{chosen_category}**")
            news_list = fetch_category_news(chosen_category)
            if news_list:
                display_news_grid(news_list[:9])  # Display in grid format
            else:
                st.info(f"No news found for category '{chosen_category}'.")
    
    elif st.session_state.page == "Search":
        st.title("Search for News 🔍")
        user_topic = st.text_input("Enter a topic:")
        if st.button("Search") and user_topic:
            user_topic_pr = user_topic.replace(" ", "+")
            news_list = fetch_news_search_topic(user_topic_pr)
            if news_list:
                st.subheader(f"Results for **'{user_topic}'**")
                display_news_grid(news_list[:9])  # Display in grid format
            else:
                st.error(f"No news found for '{user_topic}'.")

# Main app
def main():
    render_navigation()
    render_page()

if __name__ == "__main__":
    main()
