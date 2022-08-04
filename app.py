from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase
import requests
import json

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["SECRET_KEY"] = "sdjn;lakdfjase;oiasejf"

config = {
  "apiKey": "AIzaSyBjZusSvudpDXISXWYcnaNLREvkf9Fv1ao",
  "authDomain": "facenotebook-524d4.firebaseapp.com",
  "databaseURL": "https://facenotebook-524d4-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "facenotebook-524d4",
  "storageBucket": "facenotebook-524d4.appspot.com",
  "messagingSenderId": "1090680881443",
  "appId":"1:1090680881443:web:859670f2c0fc3c3669cc96",
  "measurementId": "G-TPZJH0QWM8"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        username = request.form['username']
        img = request.form['img']
        bio = request.form['bio']
        check = db.child('Users').get().val()
        for i in check:
            if check[i]['username'] == username:
                print('you need a unique username')
                return render_template('signup.html')     
        try:
            user = {"email":email,"password":password,"name":name,"username":username,"bio":bio,"img":img}
            login_session['user']= auth.create_user_with_email_and_password(email, password)
            db.child('Users').child(login_session['user']["localId"]).set(user)
            return redirect(url_for('login'))
        except:
            print("Authentication error")
    return render_template("signup.html")

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if 'login' in request.form:
            email = request.form['email']
            password = request.form['password']
            try:
                login_session['user'] = auth.sign_in_with_email_and_password(email, password)
                return redirect(url_for('home'))  
            except:
                print("Authentication error")
                return render_template('login.html')
        else:
            return redirect(url_for('signup'))

    else:
        return render_template('login.html')



@app.route('/home', methods=['GET', 'POST'])
def home():
    response = requests.get("https://api.kanye.rest")
    parsed_content = json.loads(response.content) 
    quote = parsed_content['quote']
    username = db.child("Users").child(login_session["user"]["localId"]).child('username').get().val()
    img = db.child("Users").child(login_session["user"]["localId"]).child('img').get().val()
    posts = db.child('Posts').get().val()
    allusers = db.child("Users").get().val()
    if request.method == "POST":
        hello = 1
        login_session['search'] = request.form['search']
        print(login_session)
        return render_template('index.html',quote = quote, img = img , username = username , posts = posts, uid = login_session['user']['localId'], allusers = allusers, hello = hello)
    else:
        hello = 0    
        return render_template('index.html', quote = quote ,users = allusers , img = img , username = username , posts = posts, uid = login_session['user']['localId'], hello = hello)



@app.route('/add_post', methods=['GET', 'POST'])
def addpost():
    if request.method == 'POST':
        title = request.form['title']
        imglink = request.form['imglink']
        text = request.form['text']
        uid = login_session['user']['localId']
        try:
            Post = {"title":title,"imglink":imglink,"text":text,"uid":uid}
            db.child('Posts').push(Post)
            return redirect(url_for('home'))
        except:
            print("Authentication error")
    return render_template('addpost.html')


@app.route('/add_friend',methods=['GET', 'POST',])
def addfriend():
    return render_template('add_friend.html')
#    frq= {login_session['search']:db.child("Users").child(login_session['user']['localId']).get().val()['username']}
#    db.child("friendreq").push(frq)
#    return render_template('add_friend.html',frq = frq,hi = frq[login_session['search']])

    


@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect('/')

@app.route('/profile')
def profile():
    response = requests.get("https://api.kanye.rest")
    parsed_content = json.loads(response.content) 
    quote = parsed_content['quote']
    username = db.child("Users").child(login_session["user"]["localId"]).child('username').get().val()
    bio = db.child("Users").child(login_session["user"]["localId"]).child('bio').get().val()
    fullname = db.child("Users").child(login_session["user"]["localId"]).child('name').get().val()
    img = db.child("Users").child(login_session["user"]["localId"]).child('img').get().val()
    posts = db.child('Posts').get().val()
    uid = login_session['user']['localId']
    user = db.child('Users').child(login_session['user']['localId']).get().val()
    return render_template('profile.html', quote = quote ,user = user , posts = posts ,uid = uid, username = username , bio = bio , fullname = fullname , img = img )

@app.route('/hello')
def hello():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)