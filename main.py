from re import split
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
import threading
import tkinter as tk
from dns.rdatatype import NULL
import requests
from bs4 import BeautifulSoup
import os 
import mysql.connector
import datetime
from mysql.connector.locales.eng import client_error


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Webmaster3d*",
    database="priceanalyzer",
    port = 3513
)
cursor = mydb.cursor(buffered=True)

def data_input(categories, title, sales, images, price, idmlm,trackingId, customerid, description, brand, model ):
    try:
        lastrundate=datetime.datetime.now()
        cursor.execute("SELECT * FROM dataproducts WHERE IDMLM='" + idmlm +"'")

        myresult = cursor.fetchall()
        if myresult:
            for x in myresult:
                sql = "UPDATE dataproducts SET sales = '"+ str(sales) +"', price = '"+ str(price) +"', lastrundate = '"+ str(lastrundate) +"' WHERE IDMLM = '"+ idmlm +"'"
                print(sql)
                cursor.execute(sql)
                mydb.commit()
        else:
            sql = "INSERT INTO dataproducts (IDMLM, trackid, title, description, category, price, customerid, sales, lastrundate, images, brand, model) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            print(sql)
            val = (idmlm, trackingId, title, str(description), categories, price, customerid,  sales,  lastrundate ,images, brand, model)
            cursor.execute(sql, val)
            mydb.commit()
            T.insert(tk.END, "   Saved data in database! \n")
            T.see(tk.END)
            
    except Exception as e:
        print(str(e))
        T.insert(tk.END, str(e) + "\n")
        T.see(tk.END)


mainWindow = Tk()
mainWindow.title("Price Analyzer")
mainWindow.geometry('700x400')
windowWidth = 700
windowHeight = 400
positionRight = int(mainWindow.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(mainWindow.winfo_screenheight()/2 - windowHeight/2)
mainWindow.geometry("+{}+{}".format(positionRight, positionDown))
mainWindow.resizable(False, False)

mainWindowTitle = Label(mainWindow, text = "Price  Analyzer", font = ("Arial Bold",30))
mainWindowTitle.place(x = 200,y = 20)

customidLBl = Label(mainWindow, text = "Customer Id", font = ("Arial", 12))
customidLBl.place(x = 30,y = 83)

customidTxt=Entry(mainWindow, width=40)
customidTxt.focus()
customidTxt.place(x = 150,y = 83)
customid=""

T = tk.Text(mainWindow, height=15, width=82)
T.place(x = 20,y = 120)

progressbar = ttk.Progressbar(mainWindow,orient=HORIZONTAL,length=610,mode='determinate')
progressbar.place(x=70, y=365)
progressbar['value']=0

pagenumlbl = Label(mainWindow, text = "1 / 1", font = ("Arial", 12))
pagenumlbl.place(x = 20,y = 365)

mainWindow.update_idletasks()
def thread_function():
    global customid
    progressval=0
    pagecount=0
    count=0
    T.insert(tk.END, "Script Starting \n")
    customid=customidTxt.get()
    customid=customid.strip(" ")
    openUrl = "https://listado.mercadolibre.com.mx/_CustId_"  + customid
    html = requests.get(openUrl)
    souppre = BeautifulSoup(html.text,"html.parser")
    pagenationA  = souppre.find_all('a', { "class" : "andes-pagination__link"})
    nopagenum = pagenationA
    if pagenationA == NULL:
        pagenationA = openUrl
    elif len(pagenationA) ==0:
        pagenationA = [openUrl]

    for pagenation in pagenationA:
        pagecount+=1
        if pagecount==len(pagenationA):
            if len(pagenationA)!=1:
                break
        if len(nopagenum)==0:
            pages = pagenation
        else:
            pages = pagenation.get('href')
        progressval = 0
        pagenumlbl['text']=str(pagecount) + " / " + str(len(pagenationA)-1)
        html2 = requests.get(pages)
        soup = BeautifulSoup(html2.text,"html.parser")
        divs  = soup.find_all('div', { "class" : "ui-search-result__image"})
        for div in divs:
            divCount = len(divs)
            progressbarStepVal = 100 / divCount
            a  = div.find('a')
            href = a.get('href')
            productlink = href
            producthtml = requests.get(productlink)
            productsoup = BeautifulSoup(producthtml.text, "html.parser")
            texts = productsoup.find_all("a",{"class": "andes-breadcrumb__link"})
            salestag = productsoup.find("span",{"class":"ui-pdp-subtitle"}).get_text()
            pricediv = productsoup.find("div",{"class", "ui-pdp-container__row ui-pdp-container__row--price"})
            pricespans = pricediv.find("span",{"class", "price-tag ui-pdp-price__part"})
            priceintspan = pricespans.find("span",{"class", "price-tag-fraction"})
            description = productsoup.find("p", {"class", "ui-pdp-description__content"})
            pricefraction = priceintspan.get_text()
            IDMLMStr = href.rsplit("/")[3]
            preIDMLM = IDMLMStr.rsplit("-")
            idmlm = preIDMLM[0] + "-" + preIDMLM[1]
            propertiesDiv = productsoup.find("div", {"class", "ui-pdp-specs__table"})
            if propertiesDiv:
                propertiesth=propertiesDiv.find_all("th")
                propertiestd=propertiesDiv.find_all("td")
                indx=0
                for th in propertiesth:
                    if th.get_text()=="Marca":
                        brand = propertiestd[indx].get_text()
                    elif th.get_text()=="Modelo":
                        model = propertiestd[indx].get_text()
                    indx+=1
            else:
                brand="Null"
                model="Null"
            category=""
            for text in texts:
                category = category+"-"+ text.get_text()
            categories = category[1:]
            trackingId =href.rsplit("tracking_id=")[1]
            title = productsoup.find("h1",{"class":"ui-pdp-title"}).get_text()
            salesarray = salestag.split()            
            if len(salesarray)>1:
                sales = salesarray[2]
            else:
                sales = 0
            price = pricefraction+"." #+pricecent
            print("Target product => "+ title + "( Processing )")
            T.insert(tk.END, "  \n")
            T.insert(tk.END, "----   New product Processing    ----\n")
            T.insert(tk.END, "  \"" + title +"\" \n")
            T.see(tk.END)
            filename=""
            count =1
            imgDiv = productsoup.find_all('figure',{"class","ui-pdp-gallery__figure"})
            
            if not os.path.isdir(customid):
                os.mkdir(customid)
            print("     Download product images => ", idmlm , "( Start )")
            T.insert(tk.END, "   Download product images => "+ idmlm + " Start \n")
            T.see(tk.END)

            fcount=0
            for img in imgDiv:
                images = img.find("img")
                try:
                    pri = images['src']
                    if not "https://" in pri:
                        image_url = images['data-srcset']
                        image_url = image_url.split()[0]
                    else:
                        image_url = images['src']               
                    filename =customid + "/" + idmlm + "/" + idmlm + "_" + str(count) + ".jpg"
                    r = requests.get(image_url)
                    if not os.path.isdir(customid+"/"+idmlm):
                        os.mkdir(customid+"/"+idmlm)
                    with open(filename, "wb+") as f: 
                        f.write(r.content) 
                        fcount += 1
                        print("       ", filename , "( Done ) ", fcount)
                        T.insert(tk.END, "       " + filename + " \n")
                        T.see(tk.END)
                        
                    count += 1                
                except:                
                    a = "null"     
            progressval += progressbarStepVal
            progressbar['value'] = progressval                 
            mainWindow.update_idletasks()       
            print("   Download product images => ", idmlm , "( Done ) ", count - 1)
            T.insert(tk.END, "   Download product images finished! \n")
            T.see(tk.END)
            print("  Saving the data in database")
            T.insert(tk.END, "   Saving the data in database \n")
            T.see(tk.END)
            images = customid + "/" + idmlm + "/" + idmlm +"&"+str(count-1) + ".jpg" 
            print(count,"  ", title)
            data_input(categories, title, sales, images, price, idmlm, trackingId, customid, description, brand, model)
            print("Target product => ", title , "( Done )") 
            T.insert(tk.END, "  Target product  >  Done <   \n")
            T.see(tk.END)
        if count<2:
            print("fail")
            T.insert(tk.END, " >>>>    Fail!   <<<< \n")
            T.see(tk.END)
        else:
            print("done")
            T.insert(tk.END, " >>>>    Finished   <<<< \n")
            T.see(tk.END)
    progressbar['value']=100                    
    startbtn["state"] = "normal"
    mainWindow.update_idletasks()
                    

def startclicked():
    global cur_thread
    x = threading.Thread(target = thread_function, args = (), daemon=True)
    cur_thread = x
    if customidTxt.get() != "" and customidTxt.get() !=" ":
        startbtn["state"] = "disabled"
        x.start()
    else:
        messagebox.showerror("Error!", "Customer id is empty! please enter the custom id.")
        customidTxt.focus()
        
def endclicked():
    mainWindow.destroy()
    
startbtn = Button(mainWindow, text="Start", command=startclicked)
startbtn.place(x = 410,y = 82)

endbtn = Button(mainWindow, text="Exit", command=endclicked)
endbtn.place(x = 590,y = 82)

mainWindow.mainloop()