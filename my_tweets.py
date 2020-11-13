import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title('Web application with streamlit')
st.markdown('This application is a streamlit dashboard to analyze sentiment of tweets')

st.cache(persist=True)
def load_data():
    data = pd.read_csv('Tweets.csv')
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

data = load_data()

st.sidebar.subheader('Sample tweet by sentiment')
random_tweet = st.sidebar.radio('', ['positive','neutral','negative'], key='tweet')
st.write(data.query('airline_sentiment == @random_tweet')['text'].sample(n=1).iat[0])

st.sidebar.subheader('Number of tweets by sentiment')
select = st.sidebar.selectbox('Type of visualization', ['Histogram','Pie chart'])
#st.write(type(visual))

# CHART 1 -- COUNT OF TWEETS
sentiment_count = data['airline_sentiment'].value_counts()
sentiment_count = pd.DataFrame({'Sentiment': sentiment_count.index, 'Tweets': sentiment_count.values})

if not st.sidebar.checkbox('Hide',True, key='chart1'):
    st.subheader('Number of tweets by sentiment')

    if select == 'Histogram':
        fig = px.bar(sentiment_count, x='Sentiment', y='Tweets', color='Tweets')
        st.plotly_chart(fig)
    else:
        fig = px.pie(sentiment_count, values='Tweets', names='Sentiment')
        st.plotly_chart(fig)

    ## CHART 1B -- TIMESERIES
    data['day'] = data['tweet_created'].dt.date
    day_count = data.groupby(['day','airline_sentiment'])['text'].count().reset_index()

    st.subheader('How many tweets are there in one day?')
    fig = px.line(day_count, x='day', y='text', color='airline_sentiment', labels={'airline_sentiment':'tweet sentiment'})
    st.plotly_chart(fig)

# CHART 2 -- GEOLOCATION
st.sidebar.subheader('What time are people tweeting?')
hour = st.sidebar.slider('', 0, 23, step=1, key='hour')
modified_data = data[data['tweet_created'].dt.hour == hour]

if not st.sidebar.checkbox('Close Map',True, key='chart2'):
    st.subheader('What time are people tweeting?')
    st.markdown(f'{len(modified_data)} tweets between {hour}:00 and {hour+1}:00 ')
    st.map(modified_data)

    if st.sidebar.checkbox('Show raw data',False):
        st.write(modified_data)

# CHART 3 -- AIRLINE Histogram
st.subheader('Airline count of tweets')
st.sidebar.subheader('Airline')
choice = st.sidebar.multiselect('', sorted(data['airline'].unique()), key='choice')

if len(choice) > 0:
    choice_data = data[data['airline'].isin(choice)]
    fig_choice = px.histogram(choice_data, x='airline', y='airline_sentiment',
                    histfunc='count', color='airline', facet_col='airline_sentiment',
                    labels={'airline_sentiment':'tweets'}, height=600)
    st.plotly_chart(fig_choice)

# CHART 4 -- WORDCLOUD
st.sidebar.subheader('Display wordcloud for what sentiment?')
word_sentiment = st.sidebar.radio('', ['positive','neutral','negative'], key='word')

if not st.sidebar.checkbox('Close Wordcloud', True, key='chart4'):
    st.subheader(f'Word cloud for {word_sentiment} sentiment')
    df = data[data['airline_sentiment']==word_sentiment]
    words = ' '.join(df['text'])
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@')])
    wordcloud = WordCloud(width=400, height=400, stopwords=STOPWORDS, background_color='white').generate(processed_words)

    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot()
