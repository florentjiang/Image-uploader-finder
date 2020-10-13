from flask import Flask, flash, redirect, url_for, render_template, request
from werkzeug.utils import secure_filename
import pickle
import math
import os
from time import gmtime, strftime
import csv
import pandas as pd
import pdb

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpeg'}

# Create the application object
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024
app.config['SECRET_KEY'] = 'secret'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method == "POST":
      file = request.files['file']
      post = request.form["message"]
      if post == "" or file.filename == "":
        flash('Description upload failed! Description cannot be void.')
        return render_template('index.html',image_path=None), 400
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        form = filename.rsplit('.', 1)[1].lower()
        file.save(filepath)
        size_in_kb = os.path.getsize(filepath)*0.001
        now = strftime("%d %b %Y %H:%M:%S", gmtime())
        with open(UPLOAD_FOLDER+'/csvfile.csv', 'a') as datafile:
            csvwriter = csv.writer(datafile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow([filename,form,str(size_in_kb),now,post])
        flash('Image upload success!')
        return render_template('index.html',image_path=None), 201
      else:
        flash('Image upload failed!')
        return render_template('index.html',image_path=None), 400
    else:
      return render_template('index.html',image_path=None)

@app.route('/search',methods=['GET', 'POST'])
def search_page():
    data = pd.read_csv(UPLOAD_FOLDER+'/csvfile.csv', header=None)
    results = []
    if request.method == "POST":
      desc = request.form["desc"]
      form = request.form["format"]
      minsize = request.form["minsize"]
      maxsize = request.form["maxsize"]
      if maxsize == "":
        maxsize = 500*1024
      else:
        maxsize = int(maxsize)
      if minsize == "":
        minsize = 0
      else:
        minsize = int(minsize)
      for item in data.values:
        if desc in item[4] and form == item[1] and minsize < item[2] and maxsize > item[2]:
          results.append([item[4],item[1],item[2]])
      length = min(20,len(results))
      return render_template('search.html', search=True, results=results, length=length)
    else:
      length = min(20,len(data.values))
      return render_template('search.html', search=False, results=data[[4,1,2]].values, length=length)

@app.errorhandler(Exception)
def handle_exception(e):
    return render_template("error.html", e=e), 500
if __name__ == "__main__":
        app.run(debug=False) #will run locally http://127.0.0.1:5000/