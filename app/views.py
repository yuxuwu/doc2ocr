import os
import glob
import subprocess
import zipfile
from flask import render_template, request, send_file
from werkzeug import secure_filename
from app import app
from wand.image import Image
from PIL import Image as PI

'''
Defines suitable file formats
'''
def is_allowed(filename):
    print("Is allowed file type")
    return '.' in filename and filename.rsplit('.',1)[1] in set(['tif', 'tiff', 'png', 'jpg', 'jpeg', 'pdf'])


'''
Converts image to PNG if not already PNG
'''
def convert_to_png(image_path):
    png_images = []
    with Image(filename=image_path, resolution=300) as image_png:
        for img in image_png.sequence:
            img_page = Image(image=img)
            png_images.append(img_page.make_blob('png'))

    return image_png


'''
Processes all flies in INPUT_FOLDER through Tesseract to PROCEESSED_FOLDER
'''
def process(temp_file, output_file):
    command = ['tesseract', temp_file, output_file, '-l', 'eng', 'pdf']
    proc = subprocess.Popen(command, stderr=subprocess.PIPE)
    proc.wait()
    

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
                #req_images = []
                filename = secure_filename(image.filename)
                input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                temp_file = output_file = os.path.join(app.config['TEMP_FOLDER'], filename.rsplit('.')[0]+".png")
                output_file = os.path.join(app.config['PROCESSED_FOLDER'], filename.rsplit('.')[0]+"-ocr")

                print("Debug: Input_file: " + input_file)
                print("Debug: Temp_file: " + temp_file)
                print("Debug: Output_file: " + output_file)

                #Saves original image file to a temporary folder
                image.save(input_file)

                #Converts original image to PNG and saves it to a temporary folder to be OCRed
                #TODO: image is closed??
                #something = convert_to_png(input_file)
                #save(filename=temp_file)
                with Image(filename=input_file, resolution=300) as image_png:
                    for img in image_png.sequence:
                        img_page = Image(image=img)
                        #req_images.append(img_page.make_blob('png'))

                        image_png.save(filename=temp_file)

                #Process input to output
                print("Debug: Processing " + image.filename)
                process(temp_file, output_file)
                print("Debug: Output_file: " + output_file+".pdf")

        zipf = zip_files(app.config['PROCESSED_FOLDER'])

        #Clean up created files
        print("Debug: Cleaning up")
        cleanup()

        try:
            return send_file('../'+app.config['ZIP_DOWNLOAD']+'batch.zip', attachment_filename=output_file.rsplit('/')[-1])

        except Exception as err:
            return str(err)