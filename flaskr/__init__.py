import os

from flask import Flask, render_template
from textblob import TextBlob
from benzinga import news_data


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    @app.route('/')
    def index():
        api_key = "e69e80cf00114fe8987838f17e7d4a7d"
        paper = news_data.News(api_key)
        stories = paper.news()

        # Extracting required fields and transforming the data
        stock_sentiments = {}
        for data in stories:
            title = data['title']
            for stock in data['stocks']:
                stock_name = stock['name']
                if stock_name not in stock_sentiments:
                    stock_sentiments[stock_name] = {
                        'titles': [title],
                    }
                else:
                    stock_sentiments[stock_name]['titles'].append(title)

        # Applying sentiment analysis and updating the sentiment flag
        for stock_name, data in stock_sentiments.items():
            titles = data['titles']
            total_polarity = 0
            num_titles = len(titles)
            for title in titles:
                analysis = TextBlob(title)
                total_polarity += analysis.sentiment.polarity
            avg_polarity = total_polarity / num_titles
            if avg_polarity > 0.1:
                data['sentiment'] = "Bullish"
            elif avg_polarity < -0.1:
                data['sentiment'] = "Bearish"
            else:
                data['sentiment'] = "Neutral"

        # Convert dictionary to list and sort the list
        stock_sentiments_sorted = sorted(
            [
                {"stock_name": stock_name, "sentiment": data["sentiment"], "titles": data["titles"]}
                for stock_name, data in stock_sentiments.items()
                if data["sentiment"] != "Neutral"
            ],
            key=lambda x: (x["sentiment"] != "Bullish", x["sentiment"] != "Bearish"),
            )

        return render_template("index.html", stock_sentiments=stock_sentiments_sorted)

    return app

