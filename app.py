import streamlit as st
from streamlit_lottie import st_lottie
from newspaper import Article
from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
from PIL import Image
import requests, io
import nltk
nltk.download("punkt")

st.set_page_config(page_title="News Summarizer", page_icon="📰", layout="wide")

# Define a function that we can use to load lottie files from a link.
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

col1, col2 = st.columns([1, 3])
with col1:
    lottie = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_2LdLki.json")
    st_lottie(lottie)

with col2:
    st.write("""# 📰News Summarizer""")


def fetch_news_search_topic(topic):
    url = f"https://news.google.com/rss/search?q={topic}"
    client = urlopen(url) # Open the url
    xml_page = client.read() # Read the content
    client.close() # Close the connection
    soup_page = soup(xml_page, "xml") # Scrape data from the website
    news_list = soup_page.find_all("item") # Find all the news items
    return news_list


def fetch_top_news():
    url = "https://news.google.com/rss"
    client = urlopen(url) # Open the url
    xml_page = client.read() # Read the content
    print(xml_page) # Print the content
    client.close() # Close the connection
    soup_page = soup(xml_page, "xml") # Scrape data from the website
    news_list = soup_page.find_all("item") # Find all the news items
    return news_list


def fetch_category_news(category):
    url = f"https://news.google.com/rss/headlines/section/topic/{category}"
    client = urlopen(url) # Open the url
    xml_page = client.read() # Read the content
    client.close() # Close the connection
    soup_page = soup(xml_page, "xml") # Scrape data from the website
    news_list = soup_page.find_all("item") # Find all the news items
    return news_list


def fetch_news_poster(poster_url):
    try:
        poster = urlopen(poster_url)
        raw_data = poster.read()
        image = Image.open(io.BytesIO(raw_data))
        st.image(image, use_column_width=True)
    except:
        image = Image.open("images/no_image.jpg")
        st.image(image, use_column_width=True)


def display_news(list_of_news, number_of_news):
    c = 0
    print(list_of_news)
    for news in list_of_news:
        c += 1
        st.write(f"**({c}) {news.title.text}**")
        news_data = Article(news.link.text)
        try:
            news_data.download() # Download the article
            news_data.parse() # Parse the article
            news_data.nlp() # Extract natural language properties from the text
        except Exception as e:
            st.error(e)
        
        col3, col4 = st.columns(2)
        with col3:
            fetch_news_poster(news_data.top_image)
        with col4:
            with st.expander(news.title.text):
                st.markdown(
                    '''<h6 style='text-align: justify;'>{}"</h6>'''.format(news_data.summary),
                    unsafe_allow_html=True)
                st.write(f"[Read more at {news.source.text}]({news.link.text})")
            st.success(f"Published Date: {news.pubDate.text}")
        if c >= number_of_news:
            break


def main():
    category = ["Select Category", "🔥Trending News", "💖Favorite Topics", "🔍Search Topic"]
    cat_option = st.selectbox("Select Category", category)
    if cat_option == category[0]:
        st.warning("Please select a category")
    
    elif cat_option == category[1]:
        st.subheader("🔥Trending News")
        number_of_news = st.slider("Number of News", min_value=1, max_value=20, step=1, value=5)
        news_list = fetch_top_news()
        display_news(news_list, number_of_news)
    
    elif cat_option == category[2]:
        fav_topics = ['Choose Topic', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        st.subheader("Select your favorite topic")
        topic_option = st.selectbox("Select Topic", fav_topics)
        if topic_option == fav_topics[0]:
            st.warning("Please select a topic")
        else:
            number_of_news = st.slider("Number of News", min_value=1, max_value=20, step=1, value=5)
            news_list = fetch_category_news(topic_option)
            if news_list:
                st.subheader(f"Here are the top {number_of_news} news for {topic_option}")
                display_news(news_list, number_of_news)
            else:
                st.error(f"No news found for {topic_option}")
    
    elif cat_option == category[3]:
        user_topic = st.text_input("Enter your search topic")
        number_of_news = st.slider("Number of News", min_value=1, max_value=20, step=1, value=5)

        if st.button("Search") and user_topic != "":
            user_topic_pr = user_topic.replace(" ", "")
            news_list = fetch_news_search_topic(topic=user_topic_pr)
            if news_list:
                st.subheader(f"Here are the top {number_of_news} news for {user_topic}")
                display_news(news_list, number_of_news)
            else:
                st.error(f"No news found for {user_topic}")
        else:
            st.warning("Please enter a topic")


if __name__ == "__main__":
    main()