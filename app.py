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
auth= firebase.auth()
db = firebase.database()
storage = firebase.storage()



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        username = request.form['username']
        imgData = request.files['img']
        bio = request.form['bio']
        liked={"a"}
        isAdmin = 'false'
        isHelper = 'false'
        check = db.child('Users').get().val()
        for i in check:
            if check[i]['username'] == username:
                print('you need a unique username')
                return render_template('signup.html')
        try:
            print("1")
            storage.child("imagesP").child(imgData.filename).put(imgData)
            print("2")
            img = storage.child("imagesP").child(imgData.filename).get_url(None)
            print("3")
            user = {"email":email,"password":password,"name":name,"username":username,"bio":bio,"img":img,"isAdmin":isAdmin,"isHelper":isHelper,"liked":liked}
            print("4")
            login_session['user']= auth.create_user_with_email_and_password(email, password)
            print(login_session['user'])
            db.child('Users').child(login_session['user']["localId"]).set(user)
            print("6")
            return redirect(url_for('login'))
        except:
            print("Authentication error")
    return render_template("signup.html")

@app.route('/', methods=['GET', 'POST'])
def login():
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
    idToken = auth.refresh(login_session['user']['refreshToken'])
    db.child('Users').child(login_session['user']["localId"]).update({"idToken":idToken})
    user = db.child("Users").child(login_session["user"]["localId"]).get().val()
    posts = db.child('Posts').get().val()
    allusers = db.child("Users").get().val()
    return render_template('index.html', quote = quote ,users = allusers , posts = posts,user = user)



@app.route('/add_post', methods=['GET', 'POST'])
def addpost():
    if request.method == 'POST':
        title = request.form['title']
        imgData = request.files['img']
        text = request.form['text']
        uid = login_session['user']['localId']
        try:
            storage.child("imagesP").child(imgData.filename).put(imgData)
            img = storage.child("imagesP").child(imgData.filename).get_url(None)
            Post = {"title":title,"img":img,"text":text,"uid":uid,"likes":0,"comments":{}}
            db.child('Posts').push(Post)
            return redirect(url_for('home'))
        except:
            print("hi")
    return render_template('addpost.html')


@app.route('/add_friend',methods=['GET', 'POST',])
def addfriend():
    return render_template('add_friend.html')



@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect('/')

@app.route('/profile/<string:usernameP>')
def profile(usernameP):
    user = db.child("Users").child(login_session["user"]["localId"]).get().val()
    response = requests.get("https://api.kanye.rest")
    parsed_content = json.loads(response.content)
    quote = parsed_content['quote']
    posts = db.child('Posts').get().val()
    allusers = db.child("Users").get().val()
    return render_template('profile.html', user = user , quote = quote ,posts = posts, allusers = allusers, usernameP = usernameP)


@app.route('/update/<string:postId>', methods=['GET', 'POST'])
def update(postId):
    if request.method == 'POST':
        title = {"title":request.form['title']}
        text = {"text":request.form['text']}
        db.child('Posts').child(postId).update(title)
        db.child('Posts').child(postId).update(text)
        return redirect('/home')
    return render_template('updatePost.html', postId = postId)



@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == "POST":
        db.child('Posts').child(request.form['delete']).remove()
    return redirect(request.form['url'])

@app.route('/deleteUser', methods=['GET', 'POST'])
def deleteUser():
    uid = request.form['delete']
    email = request.form['email']
    password = request.form['password']
    emailC = request.form['emailC']
    passwordC = request.form['passwordC']
    if request.method == "POST":
        login_session['user'] = None
        auth.current_user = None
        login_session['user'] = auth.sign_in_with_email_and_password(email,password)
        idToken = auth.refresh(login_session['user']['refreshToken'])
        db.child('Users').child(login_session['user']["localId"]).update({"idToken":idToken})
        auth.delete_user_account(login_session['user']['idToken'])
        login_session['user'] = None
        auth.current_user = None
        login_session['user'] = auth.sign_in_with_email_and_password(emailC,passwordC)
        db.child('Users').child(uid).remove()
        for i in db.child('Posts').get().val().keys():
            if db.child('Posts').child(i).child('uid').get().val() == uid:
                db.child('Posts').child(i).remove()
    if emailC == email:
        return redirect('/')
    else:
        return redirect('home')


@app.route('/like',methods=['GET', 'POST'])
def like():
    like = {"likes":db.child('Posts').child(request.form['post']).child('likes').get().val()+1}
    dislike = {"likes":db.child('Posts').child(request.form['post']).child('likes').get().val()-1}
    liked = db.child('Users').child(login_session["user"]["localId"]).child('liked').get().val()
    if request.form['post'] in liked:
        db.child('Posts').child(request.form['post']).update(dislike)
        liked.remove(request.form['post'])
        db.child('Users').child(login_session["user"]["localId"]).update({'liked':liked})
    else:
        db.child('Posts').child(request.form['post']).update(like)
        liked.append(request.form['post'])
        db.child('Users').child(login_session["user"]["localId"]).update({'liked':liked})
    return redirect(request.form['url'])

@app.route('/searchFU',methods=['GET', 'POST'])
def searchFU():
    username = request.form['search']
    for i in db.child('Users').get().val().keys():
        if db.child('Users').child(i).child('username').get().val() == username:
            print(username)
            return redirect("profile/"+username)
    print("user not Found")
    return redirect('home')






if __name__ == '__main__':
    app.run(debug=True)
