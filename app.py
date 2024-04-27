from flask import Flask, render_template, request, jsonify
import os 
import tensorflow.keras.backend as K
from deeplearning import OCR
from CustomOCR import customocr
from DBinterface import check_car_existence, insert_row
from datetime import datetime, timedelta
# webserver gateway interface
app = Flask(__name__)

BASE_PATH = os.getcwd()
UPLOAD_PATH = os.path.join(BASE_PATH,'static/upload/')

def separate_letters(input_string):
    result = ''
    for i, char in enumerate(input_string):
        if char.isalnum() or (i != 0 and char != ' '):
            result += char + ' '
    return result.strip()
@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        upload_file = request.files['image_name']
        filename = upload_file.filename
        path_save = os.path.join(UPLOAD_PATH,filename)
        upload_file.save(path_save)
        easyOCRtext = OCR(path_save,filename)
        roiPath = './static/roi/{}'.format(filename)
        CustomOCRtext = customocr(roiPath)
        return render_template('index.html',upload=True,upload_image=filename,easyOCRtext=easyOCRtext , customOCRtext = CustomOCRtext) 

    return render_template('index.html',upload=False) 



@app.route('/upload_image', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No file part'
        upload_file = request.files['image']
        if upload_file.filename == '':
            return 'No selected file'
        filename = upload_file.filename
        path_save = os.path.join(UPLOAD_PATH, filename)
        upload_file.save(path_save)
        #number_plate = OCR(path_save, filename)
        roiPath = './static/roi/{}'.format(filename)
        CustomOCRtext = customocr(roiPath)
        CarNum = separate_letters(CustomOCRtext)
        if(check_car_existence(CarNum)):
            # Get the current date and time
            current_datetime = datetime.now()

            # Calculate the departure datetime (current datetime + 3 hours)
            departure = current_datetime + timedelta(hours=3)

            # Format the arrival and departure datetimes as strings
            arrival_str = current_datetime.strftime('%Y-%m-%d')
            departure_str = departure.strftime('%Y-%m-%d')
            position = 'A1'
            insert_row('standard_garage_info',CarNum)
            return "True"
        else:
            return "False"

        

if __name__ =="__main__":
    app.run(debug=True)