from webapp import app, db
import random
from webapp.models import User
from werkzeug.urls import url_parse
from webapp.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, url_for, request, session, redirect, flash
from pymongo import MongoClient 
import json,csv
from bson import json_util
from json2html import *
from bson.json_util import dumps
import uuid,os
import pandas as pd
from webapp.xlsx import extract_xlsx
from webapp.csv_file import extract_csv

from webapp.xlsx1 import extract_xlsx1
from webapp.csv_file1 import extract_csv1
from werkzeug.utils import secure_filename
import pymongo
global flagExport 
global flagImport
import copy
from xlrd import open_workbook



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.save()
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login',page = 1))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home',page = 1)
        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/home/<string:page>')
@login_required
def home(page = 1):

    client = MongoClient()
    db = client.databaseFor2
    collection = db.data
    i = page
    cursor = collection.find({}).skip((int(page)*5)-5).limit(5);

    dataSent = dumps(cursor, sort_keys=True, indent=4, default=json_util.default)
    print("*****************************************************")
    for document in cursor:
          print(document)
    print("**************************************")
    
    
    
    # print(dataSent)
    list_of_entities = json2html.convert(json=dataSent)
    return render_template('index.html',dataSent=list_of_entities)



@app.route('/addData',methods = ['GET','POST'])
def addData():
    
    form_data = [str(x) for x in request.form.values()]
    parameter = form_data[0]
    source = form_data[1]
    print(len(form_data))
    impact = form_data[2]
    datatype = form_data[3]
    weightage = form_data[5]
    mappingfield = form_data[6]
    
    
    print(parameter)
    print(source)
    print(impact)
    print(datatype)
    print(weightage)
    print(mappingfield)
    
    # Python code to illustrate 
    # inserting data in MongoDB 

    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except: 
        print("Could not connect to MongoDB") 

    db = conn.databaseFor2 

    collection = db.data 
    
    last =collection.find_one({},
    sort=[( '_id', pymongo.DESCENDING )]
    ) 
    last_id = last['_id'] 
    _id  = int(last_id) + 1  


    print("Lasr row", _id)
    print("**********************************")


    elementedData = {
        '_id':_id,
        "Parameter": parameter,
        "Source": source,
        "Impact" : impact,
        "Datatype": datatype,
        "Weightage":weightage,
        "Mappingfield":mappingfield
    }

    # Insert Data 
    rec_id1 = collection.insert_one(elementedData) 
    return redirect(url_for('home'))


@app.route("/test",methods=['POST','GET'])
def test():
    return render_template("add.html")

@app.route("/export", methods = ['GET','POST'])
def export():
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except: 
        print("Could not connect to MongoDB") 

    db = conn.databaseFor2 
    collection = db.data.find({})

    dataSent = dumps(collection, sort_keys=True, indent=4, default=json_util.default)
    dataSent = json.loads(dataSent)
    
    # print(dataSent)
    # for i in range(0,len(dataSent)):
    #     dataSent[i]["_id"] = dataSent[i]["_id"]["$oid"]
       
    pd.read_json(json.dumps(dataSent)).to_csv('pandas.csv')
    
    print(type(dataSent))
    export_status = "File Exported"
    flagExport = 1
    return redirect('home/1') 
    
    
    
@app.route('/page',methods = ['GET','POST'])
def import_data():
    if request.method == 'POST':
        f = request.files['file']
        print("Inside Import")

    
    ROOT_DIR = os.path.abspath(os.curdir)
    if not os.path.exists(f.filename):        
        f.save(secure_filename(f.filename))
        
    name_of_file = f.filename      
    file_path = os.path.join(ROOT_DIR,name_of_file)
    extension = os.path.splitext(name_of_file)[1]
    
    if extension == ".xlsx":
        extract_xlsx(file_path)
                    
    elif extension == ".csv":
        extract_csv(file_path,name_of_file)
        print("Inside csv")
        
    import_status = "File Successfully uploaded"
    flagImport = 1
        
    return redirect('home/1')


@app.route('/newpage',methods = ['GET','POST'])
def newpage():
    return render_template('page.html')



@app.route('/paginationForward',methods = ['GET','POST'])
def paginationForward():
    rule = request.referrer
    comp_url = str(rule)
     
    u = comp_url.rindex('/')
    print(u)
    
    number = comp_url[u+1:]
    try:        
        number = int(number)   
    except:
        number = 1 
    number = number +1        

    return redirect('home/'+str(number))




@app.route('/paginationbackward',methods = ['GET','POST'])
def paginationbackward():
    rule = request.referrer
    comp_url = str(rule)
     
    u = comp_url.rindex('/')
    print(u)
    number = comp_url[u+1:]
    try:        
        number = int(number)   
    except:
        number = 1 
    

    
    if number == 1 or len(str(number))>2:
        number =1
    else:
        number = number -1   
        
    return redirect('home/'+str(number))




def csv_to_json(filename, header=None):
    data = pd.read_csv(filename)
    data = data.applymap(str)
    return data.to_dict('records')




    


@app.route('/uploadfunctionality')
def uploadfunctionality():
    return render_template('page1.html')

@app.route('/predict',methods=['POST'])
def predict():

    if request.method == 'POST':
        f = request.files['file']

        ROOT_DIR = os.path.abspath(os.curdir)
        name_of_file = f.filename 
        formatted_name = name_of_file.replace(" ","")
        


        f.save(formatted_name)
       
        file_path = ROOT_DIR+"/"+formatted_name
        print("Its Done")

        extension = os.path.splitext(formatted_name)[1]
       
        if extension == ".xlsx":
            extract_xlsx1(file_path)
                        
        elif extension == ".csv":
            extract_csv1(file_path,name_of_file)


        
    return render_template('page1.html', status = "document recieved")


@app.route('/updatevalue', methods = ['GET','POST'])
def updatevalue():  
    return render_template("update.html")
    
    
@app.route('/updateparameter',methods = ['GET','POST'])
def updateparameter():
    form_data = [str(x) for x in request.form.values()]
    id = form_data[0]
    parameter = form_data[1]
    source = form_data[2]
    print(len(form_data))
    impact = form_data[3]
    datatype = form_data[4]
    weightage = form_data[6]
    mappingfield = form_data[7]
    
    
    try: 
        conn = MongoClient() 
        print("Connected successfully!!!") 
    except: 
        print("Could not connect to MongoDB") 

    db = conn.databaseFor2 

    collection = db.data 
    
    

    doc = collection.find_one_and_update(
        {"_id" :id},
        {"$set":
            {'_id':id,
        "Parameter": parameter,
        "Source": source,
        "Impact" : impact,
        "Datatype": datatype,
        "Weightage":weightage,
        "Mappingfield":mappingfield}
        },upsert=True
    )

    
    
    
    
    
    return redirect('home/1')
