from flask import Flask, render_template
from textblob import TextBlob
from benzinga import news_data
from textblob import TextBlob
from . import app

@app.route("/")
def home():
    return "Hello"

api_key = "e69e80cf00114fe8987838f17e7d4a7d"
paper = news_data.News(api_key)
stories = paper.news()

# Creating a dictionary to store titles related to each unique stock name
stock_titles = {}

# Extracting the title and the corresponding stock names
for item in stories:
    title = item['title']
    stock_names = [stock['name'] for stock in item['stocks']]
    for stock_name in stock_names:
        if stock_name not in stock_titles:
            stock_titles[stock_name] = [title]
        else:
            stock_titles[stock_name].append(title)

# Perform sentiment analysis for each stock based on all titles
for stock_name, titles in stock_titles.items():
    total_polarity = 0
    num_titles = len(titles)

    for title in titles:
        analysis = TextBlob(title)
        total_polarity += analysis.sentiment.polarity

    avg_polarity = total_polarity / num_titles

    if avg_polarity > 0.1:
        sentiment = "Bullish"
    elif avg_polarity < -0.1:
        sentiment = "Bearish"
    else:
        sentiment = "Neutral"

@app.route('/screener')
def index():
    stock_sentiments = []
    for stock_name, titles in stock_titles.items():
        total_polarity = 0
        num_titles = len(titles)

        for title in titles:
            analysis = TextBlob(title)
            total_polarity += analysis.sentiment.polarity

        avg_polarity = total_polarity / num_titles

        if avg_polarity > 0.1:
            sentiment = "Bullish"
        elif avg_polarity < -0.1:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"

        stock_sentiments.append({
            'stock_name': stock_name,
            'titles': titles,
            'sentiment': sentiment
        })

        # Sort the list by sentiment
        stock_sentiments_sorted = sorted(stock_sentiments, key=lambda x: x['sentiment'])

    return render_template("index.html", stock_sentiments=stock_sentiments_sorted)