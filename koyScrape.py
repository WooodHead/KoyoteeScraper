import praw, re, os

r = praw.Reddit(user_agent="KoyoteeScraper v0.2 by /r/slomobob")
bookDictionary={"The Saga Begins":"https://www.reddit.com/r/Koyoteelaughter/comments/2vj3t4/croatoan_earth_the_saga_begins_table_of_contents/",
                "Tatooed Horizon":"https://www.reddit.com/r/Koyoteelaughter/comments/2wlm5d/croatoan_earth_tattooed_horizon_table_of_contents/",
                "Warlocks":"https://www.reddit.com/r/Koyoteelaughter/comments/33vh4q/croatoan_earth_warlocks_table_of_contents/",
                "Church of Echoes(INCOMPLETE)":"https://www.reddit.com/r/Koyoteelaughter/comments/4rmt1t/croatoan_earth_church_of_echoes_table_of_contents/"
                }
author = "Koyoteelaughter"
text = ""
pageList = []
uuid = ""
bookTitle = ""


def createPartHTML(partLinkTuple):
    """removes 0-2 <hr> tags and everything below them.
        then writes html file
        currently leaves the title in(not linked, either), will prob change later
    """
    title = partLinkTuple[0]
    url = partLinkTuple[1]
    f = open(title.replace(" ","")+".xhtml",'w')
    sub = r.get_submission(url.replace("http","https").replace("httpss","https")) #redirects, man
    t = sub.selftext_html
    tx = re.split(r'(?:\<hr\/\>(?:.|\n)*){0,2}$',t)[0]
    f.write(tx)
    f.close()

def writeContentFile(f,bookTitle,uuid,author,pageList):
    """I didn't want to look at this anymore, sorry :-/
    """
    #Write metadata block
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookID" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>"""+bookTitle+"""</dc:title>
	<dc:language>en</dc:language>
    <dc:creator opf:role="aut">"""+author+"""</dc:creator>
    <dc:identifier id="BookID" opf:scheme="UUID">"""+uuid+"""</dc:identifier>
    </metadata>\n""")
    
    #Manifest
    f.write("""<manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        """)
    for l in pageList:
        page = l[0].replace(" ","")+".xhtml"
        f.write('''        <item id="'''+page+'''" href="Text/'''+page+'''" media-type="application/xhtml+xml"/>\n''')   
    f.write("</manifest>\n")
    
    #Spine
    f.write("""<spine toc="ncx">\n""")
    for l in pageList:
        page = l[0].replace(" ","")+".xhtml"
        f.write('''    <itemref idref="'''+page+'''"/>\n''')
    f.write("""</spine>
</package>""")
    #OMG finally
    
def buildSkeleton(bookTitle,uuid,author,pageList):
    """ takes care of all the boilerplate the content will be put into """
    os.mkdir(bookTitle)
    os.chdir(bookTitle)
    os.makedirs(r'./META-INF')
    os.makedirs(r'./OEBPS/Text')
    
    f = open("mimetype",'w')
    f.write("application/epub+zip")
    f.close()
    
    f = open("./META-INF/container.xml", 'w')
    f.write("""<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>""")
    f.close()
    
    #content.opf
    f = open("./OEBPS/content.opf",'w')
    writeContentFile(f,bookTitle,uuid,author,pageList)
    f.close()
    
    #Table of Contents
    f = open("./OEBPS/toc.ncx",'w')
    f.write('''<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">

<head>
    <meta name="dtb:uid" content="'''+uuid+'''"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    
    <docTitle>
        <text>'''+bookTitle+'''</text>
    </docTitle>
    \n''')
    
    f.write("<navMap>\n")
    i = 1
    for l in pageList:
        f.write('''    <navPoint id="'''+l[0].replace(" ","")+'''" playOrder="'''+str(i)+'''">
        <navLabel>
            <text>'''+l[0]+'''</text>
        </navLabel>
        <content src="Text/'''+l[0].replace(" ","")+".xhtml"+'''"/>
        </navPoint>\n''')
        i+=1
    f.write("</navMap>\n")
    f.close()
        
def makeEpub(bookTitle):
    import sys    
    sys.path.append(os.getcwd())
    import zipfile
    
    z = zipfile.ZipFile(bookTitle+".zip",'w',zipfile.ZIP_STORED)
    z.write("./"+bookTitle+"/mimetype","mimetype")
    z.close()

    z = zipfile.ZipFile(bookTitle+".zip",'a',zipfile.ZIP_DEFLATED)
    z.write("./"+bookTitle+"/META-INF/container.xml","META-INF/container.xml")
    z.write("./"+bookTitle+"/OEBPS/toc.ncx","OEBPS/toc.ncx")
    z.write("./"+bookTitle+"/OEBPS/content.opf","OEBPS/content.opf")


    parts = tuple(os.walk(bookTitle+"/OEBPS/Text/"))[0][2]  #freakin generators
    for p in parts:
        z.write(bookTitle+"/OEBPS/Text/"+p,"OEBPS/Text/"+p)
    z.close()

    import shutil
    shutil.rmtree("./"+bookTitle, ignore_errors=True)
    shutil.rmtree("./"+bookTitle, ignore_errors=True)
    os.rename(bookTitle+".zip",bookTitle+".epub")   

def setTarget(title,bookDictionary):
    global text, pageList, uuid, bookTitle
    book = r.get_submission(url=bookDictionary.get(title))
    text = book.selftext
    pageList = re.findall(r'\[(\w+ ?\w*) {0,2}\]\( ?(https?://\w{2,3}.reddit.com[^)]+)\)', text)  #a list of tuples containing the text(if only two words) and url linking to each part
    uuid = "Koyoteelaughter-Croatoan-Reddit-"+title+"-v0"
    bookTitle = title
    
    
def main():
    buildSkeleton(bookTitle,uuid,author,pageList)
    os.chdir("./OEBPS/Text")
    for l in pageList:
        createPartHTML(l)
        print l[0]
    os.chdir("../../../")   #back up 'above' the top folder
    makeEpub(bookTitle)
    
for k in bookDictionary.iterkeys():
    print "~~~"+k+"~~~"
    setTarget(k,bookDictionary)
    main()