from flask import Blueprint, render_template, request, redirect, session, url_for
import pymongo, bcrypt

auth = Blueprint('auth', __name__)

client = pymongo.MongoClient("mongodb+srv://srm:2024@cluster0.ec8b1tz.mongodb.net/test")
db = client.get_database('total_records')
records = db.register


@auth.route('/signup/', methods = ['GET', 'POST'])
def sign_up():
    if "user" in session:
        return redirect(url_for('/dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')

        password = request.form.get('password')
        confirm_pass = request.form.get('confirm_pass')
        #Checking whether email is already registered or not
        email_found = records.find_one({"email":email})
        
        if email_found:
            message = 'This email already exists'
            return redirect(url_for('/login'), message = message )

        if password!=confirm_pass:
            message = 'Passwords should match!'
            return render_template('signup.html',message = message)
        
        else:
            
            #hashing the password and encoding it
            hashed = bcrypt.hashpw(confirm_pass.encode('utf-8'), bcrypt.gensalt())

            #assigning the data in a dictionary in key value pairs
            user_input = {'email': email, 'name': name, 'password': hashed}
            #inserting it in the record collection
            records.insert_one(user_input)
            message = 'successfully sent :)'
    return render_template('signup.html', message = message)


@auth.route('/', methods = ['GET', 'POST'])
def index():
    message = ""
    if 'user' in session:
        print('check123')
        return redirect(url_for('/dashboard'))
    if request.method == 'POST':
        user = request.form.get('email')
        password = request.form.get('password')
        user_found = records.find_one({'email':user})
        if user_found:

            passwordcheck = user_found['password']
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["emailid"] = user
                message = "Welcome user "
                return redirect('/dashboard')
            else:
                message = "Wrong password"
                return render_template('login.html',message = message)
        else:
            message = 'User not found'
            return render_template('login.html', message = message)
    return render_template('login.html', message = message)

@auth.route('/dashboard/')
def dashboard():
    if 'user' in session:
        user = session['user']
        return render_template('dashboard.html')
    else:
        message = 'Please login into your account!'
        return render_template('dashboard.html') #redirect(url_for('login'))
    #return render_template('dashboard.html', message = message)


@auth.route("/logout/")
def logout():
    if "user" in session:
        session.pop("user", None)
        return redirect('/')
    else:
        return redirect('/')


@auth.route("/cam/")
def cam():
    if "user" in session:
        return render_template('cam.html')
    else:
        return render_template('cam.html')

@auth.route('/attendance')
def att():
    return render_template('attendance.html')