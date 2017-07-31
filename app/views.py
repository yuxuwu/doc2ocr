import os
from flask import render_template, request
from werkzeug import secure_filename
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                            title='Home',
    )

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'file uploaded successfully'
