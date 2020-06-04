from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup as bs
import pymongo
from flask_bootstrap import Bootstrap
app = Flask(__name__)
Bootstrap(app)
@app.route("/", methods=["POST","GET"])

def index():
    if request.method == "POST":
        searchString=request.form['content'].replace(" ","")
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            db = dbConn['Textreview']
            reviews = db[searchString].find({})
            if reviews.count()> 0:
                reviews = list(reviews)
                return render_template('result.html', reviews=reviews)
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString
                r = requests.get(flipkart_url)
                flipkart_html = bs(r.content, "html.parser")
                bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})
                del bigboxes[0:3]
                box = bigboxes[0]
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                prodRes = requests.get(productLink)
                prod_html = bs(prodRes.text, "html.parser")
                reviews = []
                table = db[searchString]
                commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"})
                print("2")
                for commentbox in commentboxes:
                    try:
                        name = commentbox.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

                    except:
                        name = 'No Name'
                    try:
                        rating = commentbox.find_all('div', {'class': 'hGSR34 E_uFuv'})[0].text
                    except:
                        rating = 'No Rating'
                    try:
                        commentHead = commentbox.find('p', {'class': '_2xg6Ul'}).text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentbox.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer Comment'

                    mydict = {'Product': searchString, 'name': name, 'rating': rating, 'commentHead': commentHead, 'custComment': custComment}
                    table.insert_one(mydict)  # insertig the dictionary containing the rview comments to the collection
                    reviews.append(mydict)  # appending the comments to the review list
                reviews = list(reviews)
                return render_template('result.html', reviews=reviews)  # showing the review to the user
        except:
            return 'You have Enter the wrong input.'
                # return render_template('results.html')

    else:
        return render_template('home.html')

if __name__=="__main__":
    app.run()