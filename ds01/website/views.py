# from flask import Blueprint, render_template, request, session, redirect, url_for
# import pymongo, bcrypt

# views = Blueprint('views', __name__)

# client = pymongo.MongoClient("mongodb://localhost:27017")
# db = client.get_database('total_records')
# records = db.register

# @views.route('/', methods = ['GET', 'POST'])
# def index():
#     message = ""
#     if request.method == 'POST':
#         user = request.form.get('email')
#         password = request.form.get('password')
#         user_found = records.find_one({'email':user})
#         if user_found:
#             passwordcheck = user_found['password']

#             if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
#                 session["emailid"] = user
#                 return redirect('/dashboard')
#             else:
#                 if 'user' in session:
#                     print('check123')
#                     return (url_for('/dashboard'))
#                 message = "Wrong password"
#                 return render_template('login.html',message = message)
#         else:
#             message = 'User not found'
#             return render_template('login.html', message = message)
#     return render_template('login.html', message = message)

# @views.route('/dashboard/')
# def dashboard():
#     if 'user' in session:
#         user = session['user']

#         return render_template('dashboard.html')
#     else:
#         message = 'Please login into your account!'
#         return redirect(url_for('login'), message = message)


# @views.route("/logout")
# def logout():
#     if "user" in session:
#         session.pop("user", None)
#         return render_template('index.html')
#     else:
#         return render_template('index.html')


# @views.route("/cam/")
# def cam():
#     if "user" in session:
#         return render_template('cam.html')
#     else:
#         return render_template('cam.html')