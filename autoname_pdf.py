import PyPDF2


# File names are to match the pattern:
#
# [title] _ [author(s) last name] _ [publisher] _ [year]
#
# Where ' _ ' is a customizable field separator.


# Program functionality:
# 1. Open specified PDF file
# 2. Run extractor(s) and extract metadata information
# 3. Discard empty or invalid data and
#    pick "best" match for each field
# 5. Assemble new file name
# 6. Check target file name for existing files, permissions, ..
# 6. Rename the file



def open_pdf(pdf_filename):
    pdfFileObj = open(pdf_filename, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    documentInfo = pdfReader.getDocumentInfo()

    title = documentInfo.title
    author = documentInfo.author
    author_lastname = author.split()[-1]

    xmpdata = pdfReader.getXmpMetadata()

    # print "documentInfo.items:"
    # for i in documentInfo.items():
    #     print(i)

    # print "XmpMetadata.items:"
    # for x in xmpdata.dc_date:
    #     print(x)


    print "title: " + title
    print "author: " + author
    print "    last name: " + author_lastname


    if title:
        print "i haz title"
    else:
        print "unknown title"


# def extract_data_with_pypdf2(pdfReader):



# open_pdf('Eclipse-IDE-Pocket-Guide_Burnette_OReilly-2005.pdf')
# pageObj = pdfReader.getPage(0)
# pageObj.extractText()
# print pageObj

# def printMeta(fileName):
#     pdfFile = PyPDF2.PdfFileReader(file(fileName, 'rb'))
#     docInfo = pdfFile.getDocumentInfo()
#
#     print '[*] PDF MetaData For: ' + str(fileName)
#
#     for metaItem in docInfo:
#         print '[+] ' + metaItem + ':' + docInfo[metaItem]


# printMeta('Eclipse-IDE-Pocket-Guide_Burnette_OReilly-2005.pdf')
