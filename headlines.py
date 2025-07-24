import feedparser
from flask import Flask, render_template, request, make_response
import json
import urllib.request
import urllib.parse
import datetime

app = Flask(__name__)

RSS_FEEDS = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640'
}

DEFAULTS = {
    'publication': 'bbc',
    'city': 'London,UK'
}

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(query):
    api_key = "f329d49ba89e71ada7320b73521b0f2f"  # Replace with your real key
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format("{}", api_key)

    query_encoded = urllib.parse.quote(query)
    url = api_url.format(query_encoded)

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
        parsed = json.loads(data)
    except urllib.error.HTTPError as e:
        print("Weather fetch failed:", e)
        return None

    if parsed.get("weather"):
        return {
            "description": parsed["weather"][0]["description"],
            "temperature": parsed["main"]["temp"],
            "city": parsed["name"],
            "country": parsed["sys"]["country"]
        }
    return None

@app.route("/")
def home():
    # get customized headlines
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    # get customized weather
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    response = make_response(render_template("index.html", articles=articles, weather=weather))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    return response

if __name__ == "__main__":
    app.run(port=5000, debug=True)
