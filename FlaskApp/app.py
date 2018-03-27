from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, send_from_directory
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#config MySQL
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='ckato..'
app.config['MYSQL_DB']='flaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#init MYSQL
mysql = MySQL(app)

Articles = Articles()

#files for js and css
""" @app.route('/includes/<path:path>')
def send_js(path):
    return send_from_directory('js',path) """

#index
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id )


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1,max=50)])
    username = StringField('UserName',[validators.Length(min=4,max=25)])
    email = StringField('Email',[validators.Length(min=6,max=50)])
    Password = PasswordField('Password',[
        validators.DataRequired(),
        validators.EqualTo('confirm',message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.Password.data))

        #Create Curser
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You are now registered, you can log in', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

#Login
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        #Get form fields
        username = request.form['username']
        password_entered= request.form['password']

        #Create cursor
        cur = mysql.connection.cursor()

        #Get user by username
        result = cur.execute('SELECT * FROM users WHERE username=%s',[username])

        if result > 0:
            #Get store hash
            data= cur.fetchone()
            password = data['password']

            #compare passwords
            if sha256_crypt.verify(password_entered, password):
                #app.logger.info('Password matched')
                #passed
                session['logged_in']=True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))

            else:
                #app.logger.info('Password did not match')
                error='Invalid login'
                return render_template('login.html',error=error)
            #close connection
            cur.close()

        else:
            #app.logger.info('No user found')
            error='No user found'
            return render_template('login.html',error=error)

    return render_template('login.html')
#check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


#logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('you are now logged out', 'success')
    return redirect(url_for('login'))

#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1,max=200)])
    body = TextAreaField('Body',[validators.Length(min=30)])

#Add article
@app.route('/Add_article', methods=['POST','GET'])
@is_logged_in
def Add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.tittle.data
        body = form.body.data

        #create cursor
        cur = mysql.connection.cursor()

        #excute
        cur.execute("INSERT INTO articles (title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Article has been created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html',form=form)


if __name__ =='__main__':
    app.secret_key='mykey123'
    app.run(debug=True)