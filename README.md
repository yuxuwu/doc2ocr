# doc2ocr
**Please visit the organize_files branch for the latest version**

*A flask application that converts documents to a searchable PDF file*

TODO:
- [x] Convert and serve one file.
- [x] Allow users to upload multiple files.
- [ ] Sort files using keywords.
- [ ] File conversion status.
- [ ] Create a front-end.

Pipeline:
1. Take in a batch of files
2. For each file:
    1. Convert to PNG format
    2. Process the file through tesseract to a PDF file
    3. Append file to a list of result PDFs
3. Zip the list of PDFs into a zip file
4. Serve zip file to user
