import os
import subprocess
from flask import render_template, request, send_file
from werkzeug import secure_filename
from app import app
from wand.image import Image
from PIL import Image as PI

def is_pdf(filename):
    print("Debug: Image is PDF")
    return '.' in filename and 'pdf' in filename.rsplit('.',1)[1] 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in set(['png', 'jpg', 'jpeg', 'pdf'])


####################################################################################

@app.route('/')
def index():
    return render_template('index.html',
                            title='Home',
                            )

@app.route('/convert', methods = ['GET', 'POST'])
def convert():
    if request.method == 'POST':
        f = request.files['file']
        req_images=[]

        if f and is_pdf(f.filename):
            filename = secure_filename(f.filename)
            input_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            temp_file = output_file = os.path.join(app.config['TEMP_FOLDER'], filename.rsplit('.')[0]+".png")
            output_file = os.path.join(app.config['PROCESSED_FOLDER'], filename.rsplit('.')[0]+"-ocr")

            print("Debug: Input_file: " + input_file)
            print("Debug: Temp_file: " + temp_file)
            print("Debug: Output_file: " + output_file)

            f.save(input_file)

            with Image(filename=input_file, resolution=300) as image_png:
                for img in image_png.sequence:
                    img_page = Image(image=img)
                    req_images.append(img_page.make_blob('png'))

                image_png.save(filename=temp_file)

            print("Debug: Processing " + f.filename)
            command = ['tesseract', temp_file, output_file, '-l', 'eng', 'pdf']
            proc = subprocess.Popen(command, stderr=subprocess.PIPE)
            proc.wait()

            print("Debug: Output_file: " + output_file+".pdf")
            print("Debug: Cleaning up")
            os.remove(input_file)
            os.remove(temp_file)
            os.remove(output_file)

            try:
                return send_file("../"+output_file+".pdf", attachment_filename=output_file.rsplit('/')[-1])

            except Exception as err:
                return str(err)
