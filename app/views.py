import os
import shutil
import glob
import subprocess
import zipfile
import yaml
import pytesseract as pyte
from app import app
from flask import render_template, request, send_file
from werkzeug import secure_filename
from wand.image import Image
from PIL import Image as IM

'''
Loads yaml config file into dictionary container
'''
def load_config(config_file):
    config_map = yaml.safe_load(config_file.read())
    print(config_map)


'''
Defines suitable file formats
'''
def is_allowed(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in set(['tif', 'tiff', 'png', 'jpg', 'jpeg', 'pdf'])


'''
Converts image to PNG if not already PNG
void return type: Files are saved to temp_file
'''
def convert_to_png(image_path, temp_image_path):
    png_images = []
    with Image(filename=image_path, resolution=300) as image_png:
        for img in image_png.sequence:
            img_page = Image(image=img)
            image_png.save(filename=temp_image_path)


'''
Converts PNG to a string(unicode)
'''
def convert_to_string(png_image):
    image = IM.open(png_image)
    return pyte.image_to_string(image.convert('RGB'))


'''
Moves file to specified folder
'''
def move_file(input_file, dest_folder):
    if not os.path.isdir(dest_folder):
        os.mkdir(dest_folder)
        shutil.move(input_file, dest_folder)


'''
Moves file to a specified folder. Creates folder if folder is not present
Parameters: input_file - file to be moved
            image_string - string contents of the file
'''
def send_to_processed(input_file, image_string):
    to_be_defaulted = True
    for folder in folder_config.keys():
        for keyword in folder_config[folder]:
            if keyword in image_string:
                to_be_defaulted = False
                dest_folder = app.config['PROCESSED_FOLDER']+folder
                move_file(input_file, dest_folder)
                return to_be_defaulted


'''
Zips a list of files into a 'batch.zip' file.
Parameters: file_list - root directory of files to be zipped
Return: a ZipFile object, stored in app.config['ZIP_DOWNLOAD']
TODO: name zipfile by UUID
'''
def zip_files(file_list):
    zipf = zipfile.ZipFile(app.config['ZIP_DOWNLOAD']+'batch.zip', 'w')
    for dirpath, dirs, files in os.walk(file_list, False):
        for folder_name in dirs:
            for file in os.listdir(os.path.join(dirpath, folder_name)):
                file_path = os.path.join(dirpath, folder_name, file)
                file_name = os.path.join(folder_name, file)
                zipf.write(file_path, arcname=file_name)
    zipf.close()
    return zipf


'''
Deletes all files in TEMP, INPUT, and OUPUT directories
'''
def cleanup():
    for file in glob.glob(app.config['UPLOAD_FOLDER']+'*'):
        os.remove(file)
    for file in glob.glob(app.config['TEMP_FOLDER']+'*'):
        os.remove(file)
    for file in glob.glob(app.config['PROCESSED_FOLDER']+'*'):
        #remove file tree 
        shutil.rmtree(file)
    #for file in glob.glob(app.config['ZIP_DOWNLOAD']+'*'):
    #    os.remove(file)

folder_config = {u"COMPLIANT": ["Page"],u"TESTS": ["Last"]}


########################################################################################################

@app.route('/')
def index():
    return render_template('index.html',
                            title='Home',
                       )

@app.route('/convert', methods = ['GET', 'POST'])
def convert():
    if request.method == 'POST':
        #Load yaml config file
        load_config(request.files['config'])
        #Datatype of image is werkzeug.datastructures.FileStorage
        for image in request.files.getlist('file'):
            #Determine if file is suitable (image file type)
            if is_allowed(image.filename):

                #Define local name variables for file names
                filename = secure_filename(image.filename)
                input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                temp_file = output_file = os.path.join(app.config['TEMP_FOLDER'], filename.rsplit('.')[0]+".png")
                output_file = os.path.join(app.config['PROCESSED_FOLDER'], filename.rsplit('.')[0])

                #Saves original image file to a temporary folder
                image.save(input_file)

                #Converts original image to PNG, then to string from its contents
                convert_to_png(input_file, temp_file)
                image_string = convert_to_string(temp_file).upper()
                #Sends orig. pdf to folder based on string contents
                to_be_defaulted = send_to_processed(input_file, image_string)
                
                if to_be_defaulted:
                    move_file(input_file, app.config['DEFAULT_FOLDER'])                    

        zipf = zip_files(app.config['PROCESSED_FOLDER'])

        #Clean up created files
        cleanup()

        try:
            zip_path = '../'+app.config['ZIP_DOWNLOAD']+'batch.zip'
            return send_file(zip_path, 
                             mimetype='application/zip',
                             as_attachment=True)

        except Exception as err:
            return str(err)