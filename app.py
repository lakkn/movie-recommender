from flask import Flask, render_template, request, url_for, flash, redirect
import pandas as pd
from recommender import *

app = Flask(__name__)

@app.route('/', methods=('GET','POST'))
def index():
  titles = []
  if request.method == "POST":
    title = request.form["title"]
    data = placeholder(title)
    print(data)
    for i in range(0,data.shape[0]):
      titles.append(data.iloc[i]["title"])
    print(titles)
  return render_template('index.html', suggestions=titles)

app.run(host='0.0.0.0', port=81)
