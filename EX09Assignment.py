# Viraj Patel
# EX09: Rotten tomatoes review extrction and analysis

# importing packages

import requests
import re
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt


review_score = []
review_info = []
review_sentiment = []

def get_reviews(url):
    headers = {'Referer': 'https://www.rottentomatoes.com/m/notebook/reviews?type=user',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
               'X-Requested-With': 'XMLHttpRequest', }

    try:
        s = requests.Session()
        req_1 = requests.get(url)
        movie_id = re.findall(r'(?<=movieId":")(.*)(?=","type)', req_1.text)[0]
    except IndexError:
        print('\nFor this particular movie please write "movie year" after your movie name.')
        movie_id = input('Enter the movie name you want to get reviews for or enter "DONE" to end:')
        movie_id = movie_id.replace(' ', '_')
        url = 'https://www.rottentomatoes.com/m/'+movie_id+'/reviews'
        s = requests.Session()
        req_1 = requests.get(url)
        movie_id = re.findall(r'(?<=movieId":")(.*)(?=","type)', req_1.text)[0]
        
    api_url = "https://www.rottentomatoes.com/napi/movie/" + movie_id + "/criticsReviews/all"

    payload = {'direction': 'next', 'endCursor': '', 'startCursor': '',}

    global review_score
    global review_info
    global review_sentiment 

    while True:
        req = s.get(api_url, headers=headers, params=payload)
        data = req.json()
        reviews = data['reviews']
        for items in reviews:
            try:
                review_info.append(items['quote'])
            except:
                review_info.append('')
                continue
            try:
                review_score.append(items['scoreOri'])
                review_sentiment.append(items['scoreSentiment'])
            except:
                review_score.append('')
                review_sentiment.append('')
                continue
        if not data['pageInfo']['hasNextPage']:
            break

        payload['endCursor'] = data['pageInfo']['endCursor']
        payload['startCursor'] = data['pageInfo']['startCursor'] if data['pageInfo'].get('startCursor') else ''
 

    return review_score, review_info, review_sentiment

def review_analysis():
    global review_score
    relevant_score = []
    stopwords = []
    stopwords_file = open('stopwords_en.txt', 'r', encoding='utf8')
    Score_normalize = {'A+':5.0,'A':4.8,'A-':4.6,'B+':4.45,'B':4.3,'B-':4.1,
                       'C+':3.95,'C':3.8,'C-':3.6,'D+':3.45,'D':3.3,'D-':3.1,
                       '5/5':5.0,'4/5':4.7,'4.0/5.0':4.7,'3.5/5.0':4.0,'3/5':4.0,
                       '2/5':3.5,'1/5':3.0,'4/4':5.0,'3.5/4':4.7,'3/4':4.5,'2/4':3.5,
                       '1/4':3.0}
    # Keeping the relevant scores according to above dictionary
    for rows in review_score:
        if rows in Score_normalize:
            relevant_score.append(rows)
        else:
            relevant_score.append('')
    # Normalizing Scores
    df = pd.DataFrame({'Review': review_info,'Score': relevant_score,'Sentiment': review_sentiment})
    df['Score'] = df['Score'].map(Score_normalize).fillna('')
    # Cleaning the reviews
    for word in stopwords_file:
        stopwords.append(word.strip())
        
    df['Review'] = df['Review'].str.lower().str.split()
    df['Review'] = df['Review'].apply(lambda x: ' '.join([word for word in x if word not in (stopwords)]))
    df['Review'] = df['Review'].str.replace('[^\w\s]','') # Remove Punctuations
    df['Review'] = df['Review'].str.split().map(lambda sl: " ".join(s for s in sl if len(s) > 3))
    
    # Top 5 Reviews
    df['Score'] = pd.to_numeric(df['Score'])
    print(df['Score'].dtype)
    pd.set_option('display.max_colwidth', -1)
    top5 = df.nlargest(5, 'Score')
    print('The Top 5 reviews are:\n', top5['Review'])
    # Bottom 5 Reviews
    bottom5 = df.nsmallest(5, 'Score')
    print('\nThe bottom 5 reviews are:\n', bottom5['Review'])
    
    # Prevalent Sentiment
    Positive = []
    Negative = []
    Nosentiment= []
    for row in df['Sentiment']:
        if row=='POSITIVE':
            Positive.append('P')
        elif row=='NEGATIVE':
            Negative.append('N')
        else:
            Nosentiment.append('No sentiment')
    if len(Positive) > len(Negative):
        print('\nThe overall sentiment of the movie is Positive.')
    elif len(Positive) == len(Negative):
        print('\nThe overall sentiment of the movie is Neutral.')
    else:
        print('\nThe overall sentiment of the movie is Negative.')
    
    # Word Cloud for top 75% of the reviews
    n = 75
    Top75percent = df.head(int(len(df)*(n/100)))
    top75reviews = Top75percent['Review']
    
    # Defining the wordcloud parameters
    wc = WordCloud(background_color="white", max_words=1000)

    # Generate word cloud
    all_words_string = ' '.join(top75reviews)
    wc.generate(all_words_string)
    
    # Show the cloud
    plt.imshow(wc)
    plt.axis('off')
    plt.show()
    
    
    # Clearing List for next movie
    review_info.clear()
    review_score.clear()
    review_sentiment.clear()
    
    
while True:
    print('\nThe movie name requirements are:')
    print('Use all lowercase alphanumeric characters')
    movie_name = input('Enter the movie name you want to get reviews for or enter "DONE" to end:')
    movie_name = movie_name.replace(' ', '_')
    if movie_name == "DONE":
        break
    get_reviews('https://www.rottentomatoes.com/m/'+movie_name+'/reviews')
    review_analysis()
    

