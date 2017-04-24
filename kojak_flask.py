from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
from werkzeug.utils import secure_filename #secure option from Flask
import os

from yummly_API import get_recipes
import kojak_controller

app = Flask(__name__) #so you can run this program just using the program name

#where you want to store images
UPLOAD_FOLDER = './file_uploads'
#set of extensions you want to allow
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
#config dictionary in flask app, ex. something you can access parameters to check max upload size
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['css'] = "./templates/css/layouts"
app.config['img'] = "./templates/img"
app.config['CROPPED'] = "./cropped_photos"

@app.route('/img/<file_name>')
def home_page(file_name):
    return send_from_directory(app.config['img'], file_name)

def allowed_file(filename):
    #split the filename so you return the first item in the list to check if its allowed
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
# check if the post request has the file part
#its an instance variable thats a dictionary to show what the page uploaded
        if 'users_img' not in request.files:
            return redirect('/')

#assign whatever is inside the files instance variable dictionary that was stored
        uploaded_img = request.files['users_img']

#if the user enters something faulty, it redirects you to homepage
        if uploaded_img.filename == '':
            return redirect('/')

#if img exists and is valid format
        if uploaded_img and allowed_file(uploaded_img.filename):
#secure the file
            filename = secure_filename(uploaded_img.filename)
            file_dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#save the file in the folder
            uploaded_img.save(file_dest)
#first argument is a string, its functions name below.
            return redirect(url_for('uploaded_file', filename=filename))

#will always be TRUE on the first iteration and show the homescreen
#the index.html has the 'form' table that allows user to POST (upload) an image,
#which will make the first if statement TRUE
    return render_template("index.html")


@app.route('/cropped_photos/<img_folder>/<file_name>')
def file_name(img_folder, file_name):
    return send_from_directory(app.config['CROPPED'], img_folder, file_name)

@app.route('/upload/<file_name>')
def upload_file_to_url(file_name): #has to match approute parameter
    #If there is an image then we can get it using the
    #send from directory function
    return send_from_directory(app.config['UPLOAD_FOLDER'], file_name)

@app.route('/bottleneck_fc_model.h5') #the bottleneck_fc_model needs to be hosted
def upload_bottleneck_fc_model():
    return send_from_directory('/bottleneck_fc_model.h5')

@app.route('/<filename>/recipe-list')
def uploaded_file(filename):
    #This function takes in a filename, and where you do your processing

    upload_file_to_url(filename)
    os.path.join(app.config['UPLOAD_FOLDER'], filename)
# This is the ENTRY POINT
# return array of ingredients
    ingredients = kojak_controller.endpoint(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#make two api calls using this array of ingredients
#1. Will find the recipes and loop through each one.
    #a. inside recipes JSON there is an ID: json["matches"][INDEX][id]
#2. b. return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    recipe_tuples = get_recipes(ingredients)
    return render_template('recipe-list.html', \
        recipe_tuples=recipe_tuples, \
        sent_in_image=("/upload/" + filename))


@app.route('/css/layouts/<css_file>')
def custom_css(css_file):
    #This allows me to get my css files from my directories
    return send_from_directory(app.config['css'], css_file)

if __name__ == "__main__":
#setting use_reloader to false solved the problem of tf running twice.
#change network IP to appropriate one!
    app.run("192.168.1.126") #, debug=True, use_reloader=False)
