from flask import Flask, render_template, request, jsonify
import os 
import tensorflow.keras.backend as K
from deeplearning import OCR
from CustomOCR import customocr
from parkingspotclassifier import parking
from DBinterface import check_car_existence, insert_row_NPR, update_SPOTS
from datetime import datetime, timedelta
# webserver gateway interface
app = Flask(__name__)

BASE_PATH = os.getcwd()
UPLOAD_PATH_NPR = os.path.join(BASE_PATH,'static/upload/NPR/')
UPLOAD_PATH_SPOTS = os.path.join(BASE_PATH,'static/upload/SPOTS/')

def separate_letters(input_string):
    result = ''
    for i, char in enumerate(input_string):
        if char.isalnum() or (i != 0 and char != ' '):
            result += char + ' '
    return result.strip()

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        if 'image_name_NPR' in request.files:
            upload_file = request.files['image_name_NPR']
            filename = upload_file.filename
            path_save = os.path.join(UPLOAD_PATH_NPR, filename)
            upload_file.save(path_save)
            easyOCRtext = OCR(path_save, filename)
            roiPath = './static/roi/NPR/{}'.format(filename)
            CustomOCRtext = customocr(roiPath)
            CustomOCRtext = separate_letters(CustomOCRtext)
            return render_template('index.html', NPR=True, upload_image=filename, easyOCRtext=easyOCRtext, customOCRtext=CustomOCRtext)
        elif 'image_name_SPOTS' in request.files:
            upload_file = request.files['image_name_SPOTS']
            filename = upload_file.filename
            path_save = os.path.join(UPLOAD_PATH_SPOTS, filename)
            upload_file.save(path_save)
            current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            
            spots = parking(
                path_save,
                current_date,
                640,
                640,
                10,
                0.5,
                0.5
            )
            update_SPOTS('standard_garage_info',spots)
            
            return render_template('index.html', SPOTS=True, upload_image=filename, current_date=current_date, spots= spots)
    return render_template('index.html', upload=False)



@app.route('/upload_image_NPR', methods=['POST'])
def upload_image_NPR():
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No file part'
        upload_file = request.files['image']
        if upload_file.filename == '':
            return 'No selected file'
        filename = upload_file.filename
        path_save = os.path.join(UPLOAD_PATH_NPR, filename)
        upload_file.save(path_save)
        #number_plate = OCR(path_save, filename)
        roiPath = './static/roi/NPR/{}'.format(filename)
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
            insert_row_NPR('standard_garage_info',CarNum)
            return "True"
        else:
            return "False"
        
@app.route('/upload_image_SPOTS', methods=['POST'])
def upload_image_SPOTS():
    
    if request.method == 'POST':
        if 'image' not in request.files:
            return 'No file part'
        upload_file = request.files['image']
        if upload_file.filename == '':
            return 'No selected file'

        filename = upload_file.filename
        path_save = os.path.join(UPLOAD_PATH_SPOTS, filename)
        upload_file.save(path_save)
        current_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        
        spots = parking(
            path_save,
            current_date,
            640,
            640,
            10,
            0.5,
            0.5
        )
           
            

        

if __name__ =="__main__":
    app.run(debug=True)