import streamlit as st
import numpy as np
import pandas as pd
from faker import Faker
import random
import plotly.express as px
#import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import base64

st.title('Hello from hxkoey!')
st.markdown('The dataset was generated using Faker, which shows user job, country, salary, age and review. Raw data can be found in the last table below.')

def create_data():
    '''Create 500 user data points'''
    random.seed(42)
    fake_gen = Faker()

    fake_profiles = []
    for i in range(500):
        first_name = fake_gen.first_name()
        salary = np.random.randint(30000,250000)
        sex = fake_gen.profile()['sex']
        country = random.choice(['Gibraltar', 'Tajikistan', 'Belize', 'Fiji', 'Lesotho'])
        job = random.choice(['Lexicographer',
                             'Programmer, applications',
                             'Physicist, medical',
                             'Theatre manager',
                             'Engineer, petroleum',
                             'Catering manager',
                             'Therapist, art',
                             'Waste management officer',
                             'Hydrogeologist'])
        review = fake_gen.text(80)
        sentiment = random.choice(['Positive', 'Neutral', 'Negative'])
        longitude = fake_gen.longitude()
        latitude = fake_gen.latitude()
        dob = fake_gen.date_of_birth()
        age = 2020 - dob.year
        dob = dob.strftime('%Y-%m-%d')

        fake_profiles.append([first_name, salary, sex, age, dob, country, job, review, sentiment, longitude, latitude])

    df = pd.DataFrame(fake_profiles, columns=['first_name', 'salary', 'sex', 'age', 'dob', 'country', 'job', 'review',\
                                          'sentiment', 'longitude', 'latitude'])

    df['longitude'] = df['longitude'].apply(float)
    df['latitude'] = df['latitude'].apply(float)

    #df.to_csv('faker.csv', index=None)
    return df

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

@st.cache(persist=True)
def load_data():
    data = create_data()
    #data = pd.read_csv('faker.csv')
    data['dob'] = pd.to_datetime(data['dob'])
    return data

data = load_data()

### CHART 1 -- SUNBURST / HISTOGRAM
st.sidebar.subheader('Chart 1: Salary Aggregation Method')
agg_method = st.sidebar.selectbox('', ['Total Salary','Average Salary'])
st.sidebar.subheader('Chart 1: Country Selection')
county_list = st.sidebar.multiselect('', sorted(data['country'].unique()))

if not st.sidebar.checkbox('Close visual chart',True):
    ## Subset data
    data_country = data[data['country'].isin(county_list)]

    ## PLOT
    if agg_method == 'Total Salary':
        fig2 = px.histogram(data_country, x='job', y='salary', color='sentiment', facet_col='country', facet_row='sex', histfunc='sum', width=900, height=600)
        st.plotly_chart(fig2)

    if agg_method == 'Average Salary':
        fig2 = px.histogram(data_country, x='job', y='salary', color='sentiment', facet_col='country', facet_row='sex', histfunc='avg', width=900, height=600)
        st.plotly_chart(fig2)


### CHART 2 -- SENTIMENT
st.sidebar.subheader('Chart 2: Sentiment')
sentiment = st.sidebar.radio('', ['Positive', 'Negative', 'Neutral'])
st.sidebar.subheader('Age Range')
age_range = st.sidebar.slider('',0,100,(20,50),step=10)

## SUBSET DATA
min_age, max_age = age_range
crit1 = data['age'] >= min_age
crit2 = data['age'] <= max_age
crit3 = data['sentiment'] == sentiment
modified_data = data[crit1 & crit2 & crit3]

if not st.sidebar.checkbox('Close map',False):
    ## PLOT
    st.subheader('Age vs Review Sentiment')
    st.markdown(f'{len(modified_data)} between the age of {min_age} and {max_age} years old with {sentiment} tweets for this time period')
    #modified_data.rename(columns={'latitude1':'lat','longitude1':'lon'}, inplace=True)
    st.map(modified_data)

### CHART 3 - WORDCLOUD
if not st.sidebar.checkbox('Close wordcloud', True):

    sentiment_df = data[data['sentiment'] == sentiment]
    words = ' '.join(sentiment_df['review'])
    #processed_words = ' '.join([word for word in words.split() if not word.startswith('@')])
    wordcloud = WordCloud(width=800, height=800, stopwords=STOPWORDS, background_color='white').generate(words)

    st.subheader(f'Displaying word cloud for {sentiment} sentiment')
    st.markdown('This may take a few moments. Please wait...')
    fig = px.imshow(wordcloud, width=700, height=700, x=None, y=None)
    fig.update_layout(
        yaxis=dict(tickvals=[]),
        xaxis=dict(tickvals=[])
    )
    st.plotly_chart(fig)

### SHOW RAW DATA
if st.sidebar.checkbox('Show raw data',True):
    st.subheader('Showing raw data below')
    st.write(data)

    with st.beta_expander("Expand to download data into CSV"):
        tmp_download_link = download_link(data, 'faker-data.csv', 'Click here to download your data!')
        st.markdown(tmp_download_link, unsafe_allow_html=True)
