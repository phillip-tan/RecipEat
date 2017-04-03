from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
import os
from yummly_API import get_recipes
from werkzeug.utils import secure_filename
import kojak_controller
app = Flask(__name__) #so you can run this program just using the program name

UPLOAD_FOLDER = './file_uploads' #where you want to store images
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']) #set of extensions you want to allow
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER #config dictionary in flask app, ex. something you can access parameters to check max upload size
app.config['css'] = "./templates/css/layouts"
app.config['img'] = "./templates/img"
app.config['CROPPED'] = "./cropped_photos"

@app.route('/img/<file_name>')
def home_page(file_name):
    return send_from_directory(app.config['img'], file_name)

def allowed_file(filename): #split the filename so you return the first item in the list to check if its allowed
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'users_img' not in request.files: #its an instance variable thats a dictionary to show what the page uploaded
            return redirect('/') # not right, would do something better, error handling

        uploaded_img = request.files['users_img'] #assign whatever is inside the files instance variable dictionary that was stored

        if uploaded_img.filename == '': #if the user enters something faulty, it redirects you to homepage
            return redirect('/')

        if uploaded_img and allowed_file(uploaded_img.filename): #if img exists and is valid
            filename = secure_filename(uploaded_img.filename) #secure the file
            file_dest = os.path.join(app.config['UPLOAD_FOLDER'], filename) #./file_uploads/img.jpg
            uploaded_img.save(file_dest) #save the file in the folder
            return redirect(url_for('uploaded_file', filename=filename)) #first argument is a string, its functions name below.

    return render_template("index.html") #will always be TRUE on the first iteration and show the homescreen
    #the index.html has the 'form' table that allows user to POST (upload) an image, which will make the first if statement TRUE

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
    #This function takes in a filename
    #This is where you do your processing
    # app.config['UPLOAD_FOLDER'], filename
    # Entry point
    # get array of ingredients
    upload_file_to_url(filename)
    os.path.join(app.config['UPLOAD_FOLDER'], filename)
    ingredients = kojak_controller.endpoint(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    recipe_tuples = get_recipes(ingredients)
    return render_template('recipe-list.html', \
        recipe_tuples=recipe_tuples, \
        sent_in_image=("/upload/" + filename))

    #make two api calls
    #1. Will find the recipes and loop through each one.
        #a. inside recipes JSON there is an ID: json["matches"][INDEX][id]
    #2.

    # ADD THIS BACK
    # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/css/layouts/<css_file>')
def custom_css(css_file):
    #This allows me to get my css files from my directories
    return send_from_directory(app.config['css'], css_file)



if __name__ == "__main__":
    app.run("192.168.1.126", debug=True)
