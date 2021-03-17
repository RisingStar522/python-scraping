from re import split
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import threading
import tkinter as tk
import requests
from bs4 import BeautifulSoup
import os 

mainWindow = Tk()
mainWindow.title("Price Analyzer")
mainWindow.geometry('700x500')
mainWindow.resizable(False, False)
mainWindowTitle = Label(mainWindow, text = "Price  Analyzer", font = ("Arial Bold", 20))
mainWindowTitle.place(x = 250,y = 30)

customidLBl = Label(mainWindow, text = "Customer Id", font = ("Arial", 12))
customidLBl.place(x = 30,y = 80)

customidTxt=Entry(mainWindow, width=40)
customidTxt.focus()
customidTxt.place(x = 150,y = 80)

T = tk.Text(mainWindow, height=20, width=82)
T.place(x = 20,y = 120)

def thread_function():
    customid=customidTxt.get()
    openUrl = "https://listado.mercadolibre.com.mx/_CustId_" + customid
    html = requests.get(openUrl)
    soup = BeautifulSoup(html.text,"html.parser")
    cc=0
    divs  = soup.find_all('div', { "class" : "ui-search-result__image"})
    T.insert(tk.END, "Script Starting \n")
    for div in divs:
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
        pricecentspan = pricespans.find("span",{"class", "price-tag-cents"})
        pricefraction = priceintspan.get_text()
        # pricecent = pricecentspan.get_text()
        IDMLMStr = href.rsplit("/")[3]
        preIDMLM = IDMLMStr.rsplit("-")
        category=""
        for text in texts:
            category = category+"-"+ text.get_text()

        categories = category[1:]
        trackingId =href.rsplit("tracking_id=")[1]
        title = productsoup.find("h1",{"class":"ui-pdp-title"}).get_text()
        sales = salestag.split()[2]
        price = pricefraction+"." #+pricecent
        idmlm = preIDMLM[0] + "-" + preIDMLM[1]

        print("Target product => "+ title + "( Processing )")
        T.insert(tk.END, "New product Processing \n")
        T.insert(tk.END, "  " + title +" \n")

        filename=""
        count =1
        imgDiv = productsoup.find_all('figure',{"class","ui-pdp-gallery__figure"})
        
        if not os.path.isdir(customid):
            os.mkdir(customid)
        print("   Download product images => ", idmlm , "( Start )")
        T.insert(tk.END, "   Download product images => "+ idmlm + " Start \n")
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
                    T.insert(tk.END, "       " + filename + " Done " + str(fcount) + " \n")
                count += 1                
            except:                
                a = "null"            
        cc += 1
        print("   Download product images => ", idmlm , "( Done ) ", count - 1)
        T.insert(tk.END, "   Download product images => "+ idmlm + " Done"+ str((count - 1))+ " \n")
        print("Target product => ", title , "( Done )") 
        T.insert(tk.END, "  "+ title + " Done \n")
    print("done")

def startclicked():
    x = threading.Thread(target = thread_function, args = (), daemon=True)
    cur_thread = x
    
    x.start()
        
def endclicked():
    mainWindow.destroy()

startbtn = Button(mainWindow, text="Start", command=startclicked)
startbtn.place(x = 420,y = 78)

endbtn = Button(mainWindow, text="Exit", command=endclicked)
endbtn.place(x = 520,y = 78)

mainWindow.mainloop()