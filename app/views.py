from app import app
import os
import glob
import subprocess
import zipfile
from flask import render_template, request, send_file
from werkzeug import secure_filename
from wand.image import Image
from PIL import Image as IM
import pytesseract as pyte

'''
Defines suitable file formats
'''
def is_allowed(filename):
    print("Is allowed file type")
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
    print(type(png_image))
    image = IM.open(png_image)
    return pyte.image_to_string(image.convert('RGB'))


'''
Processes all flies in INPUT_FOLDER through Tesseract to PROCEESSED_FOLDER
def process(temp_file, output_file):
    command = ['tesseract', temp_file, output_file, '-l', 'eng', 'pdf']
    proc = subprocess.Popen(command, stderr=subprocess.PIPE)
    proc.wait()
'''


'''
Zips a list of files into a 'batch.zip' file.
'''
def zip_files(file_list):
    zipf = zipfile.ZipFile(app.config['ZIP_DOWNLOAD']+'batch.zip', 'w')
    for f in glob.glob(file_list+'*'):
        zipf.write(f)
    zipf.close()
    return zipf


'''
Deletes all files in TEMP, INPUT, and OUPUT directories
'''
def cleanup():
    print(app.config['UPLOAD_FOLDER'])
    for file in glob.glob(app.config['UPLOAD_FOLDER']+'*'):
        os.remove(file)
    for file in glob.glob(app.config['TEMP_FOLDER']+'*'):
        os.remove(file)
    for file in glob.glob(app.config['PROCESSED_FOLDER']+'*'):
        os.remove(file)

test_folder_config = {"PART": "Page","TESTS": "Last"}


########################################################################################################

@app.route('/')
def index():
    return render_template('index.html',
                            title='Home',
                       )

@app.route('/convert', methods = ['GET', 'POST'])
def convert():
    if request.method == 'POST':
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

                #Converts original image to PNG, then to string
                convert_to_png(input_file, temp_file)
                image_string = convert_to_string(temp_file)
                print(image_string)
                input()


        zipf = zip_files(app.config['PROCESSED_FOLDER'])

        #Clean up created files
        cleanup()

        try:
            return send_file('../'+app.config['ZIP_DOWNLOAD']+'batch.zip', attachment_filename=output_file.rsplit('/')[-1])

        except Exception as err:
            return str(err)