# doc2ocr
*A flask application that converts documents to a searchable PDF file*

TODO:
- [x] Convert and serve one file.
- [x] Allow users to upload multiple files.
- [ ] Sort files using keywords.
- [ ] File conversion status.
- [ ] Create a front-end.

TODO:
Remove pdf file functionality and return text of each file
Render template passing in data of each file 
    ex. render_template("files.html", files=files)
Find a way to interpret .yaml files

Pipeline:
1. Take in a batch of files
2. Take in a text file containing keyword specifications
3. For each file:
    1. Convert to PNG format
    2. Process the file through tesseract to a text format
    3. For each keyword, search through the string for a match
    4. First keyword on match, save to designated folder defined ^^
4. Zip the root directory of prcoessed files into
5. Serve zip file to user

PDF->PNG->String->Search()->Save->Serve user


