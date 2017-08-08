# doc2ocr
*A flask application that converts documents to a searchable PDF file*

TODO:
- [x] Convert and serve one file.
- [x] Allow users to upload multiple files.
- [x] Sort files using keywords.
- [ ] File conversion status.
- [ ] Create a front-end.

ISSUES:
- [ ] Defaulted files not being sent to manual sorting directory

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


