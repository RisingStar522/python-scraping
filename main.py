from re import split
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
import threading
import tkinter as tk
import requests
from bs4 import BeautifulSoup
import os 
import mysql.connector
import datetime

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="priceanalyzer"
)
cursor = mydb.cursor(buffered=True)

def data_input(categories, title, sales, images, price, idmlm,trackingId, customerid, description ):
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
            sql = "INSERT INTO dataproducts (IDMLM, trackid, title, description, category, price, customerid, sales, lastrundate ,images) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            print(sql)
            val = (idmlm, trackingId, title, description, categories, price, customerid,  sales,  lastrundate ,images  )
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
progressbar = ttk.Progressbar(mainWindow,orient=HORIZONTAL,length=660,mode='determinate')
progressbar.place(x=20, y=365)
progressbar['value']=0
mainWindow.update_idletasks()
def thread_function():
    global customid
    progressval=0
    count=0
    T.insert(tk.END, "Script Starting \n")
    customid=customidTxt.get()
    customid=customid.strip(" ")
    openUrl = "https://listado.mercadolibre.com.mx/_CustId_" + customid
    html = requests.get(openUrl)
    soup = BeautifulSoup(html.text,"html.parser")
    cc=0
    divs  = soup.find_all('div', { "class" : "ui-search-result__image"})
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
        descriptiontag = productsoup.find("p", {"class", "ui-pdp-description__content"})
        description = descriptiontag.get_text()
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
                    progressval += 0.5
                    progressbar['value']=progressval                    
                    mainWindow.update_idletasks()
                    
                count += 1                
            except:                
                a = "null"            
        cc += 1
        print("   Download product images => ", idmlm , "( Done ) ", count - 1)
        T.insert(tk.END, "   Download product images finished! \n")
        T.see(tk.END)
        print("  Saving the data in database")
        T.insert(tk.END, "   Saving the data in database \n")
        T.see(tk.END)
        images = customid + "/" + idmlm + "/" + idmlm +"&"+str(count-1) + ".jpg"
        data_input(categories, title, sales, images, price, idmlm, trackingId, customid, description)
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
    
# def stop():
#     # global cur_thread
#     x = cur_thread
#     x.do_run = False
#     x.join()

startbtn = Button(mainWindow, text="Start", command=startclicked)
startbtn.place(x = 410,y = 82)

# stopbtn = Button(mainWindow, text="Stop", command=stop)
# stopbtn.place(x = 500,y = 82)

endbtn = Button(mainWindow, text="Exit", command=endclicked)
endbtn.place(x = 590,y = 82)


mainWindow.mainloop()