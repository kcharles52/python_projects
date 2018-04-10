from flask import Flask, render_template, request, session, logging, flash, redirect, url_for
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
from forms import RegisterForm, LoginForm, BusinessForm

app = Flask(__name__)

#configuration for the app
app.config.from_object('config')

#confif MySql
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='ckato..'
app.config['MYSQL_DB']='weconnect'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#init MYSQL
mysql = MySQL(app)

#index page
@app.route('/')
def index():
    return render_template('pages/index.html')
    #return render_template('newdesign.html')

#about us
@app.route('/about')
def about():
    return render_template('pages/about.html')

#Business
@app.route('/businesses')
def businesses():
    #create cursor
    cur= mysql.connection.cursor()

    #execute querry- find all businesses
    result= cur.execute("select * from businesses")

    businesses_list =  cur.fetchall()
    if result >0:
        return render_template('pages/businesses.html', businesses =businesses_list)
    else:
        msg = 'No business found'
        return render_template('/pages/businesses.html',msg=msg)

#single business
@app.route('/single_business/<string:id>')
def single_business(id):

    #create cursor
    cur= mysql.connection.cursor()

    #execute querry- find all businesses
    cur.execute("select * from businesses where id=%s",[id])

    Selected_business =  cur.fetchone()

    return render_template('pages/single_business.html', business =Selected_business)



#User register
@app.route('/register', methods=['POST','GET'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name = form.name.data
        email= form.email.data
        username=form.username.data
        password =sha256_crypt.encrypt(str(form.password.data))

        #create cursor
        cur = mysql.connection.cursor()

        #execute querry
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s,%s, %s, %s)",(name,email,username,password))

        #commit
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You are now registered, you can log in', 'success')

        return redirect(url_for('login'))

    return render_template('/forms/register.html', form=form)


#User login
@app.route('/login', methods=['POST','GET'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        #gettting form fields
        username = request.form['username']
        password_entered = request.form['password']

        #create cursor to execute querries
        cur = mysql.connection.cursor()

        #execute querry. Get user by name
        result = cur.execute('SELECT * FROM users WHERE username=%s',[username])

        #Check for querry results
        if result>0:
            #get stored hashed password
            data = cur.fetchone()
            password = data['password']

            #compare passwords
            if sha256_crypt.verify(password_entered,password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')

                #redirect to a dashboard
                return redirect(url_for('businesses'))
            else:
                error ='invalid login'
                return render_template('/forms/login.html',form=form,error=error)
            #close connection to db
            cur.close()
        else:
            error ='User not found, check details and login again'

            return render_template('/forms/login.html',form=form,error=error)



    return render_template('/forms/login.html', form=form)

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

#Creating a business
@app.route('/addbusiness', methods=['POST','GET'])
@is_logged_in
def addbusiness():
    form = BusinessForm(request.form)
    if request.method =='POST':
        title = form.title.data
        bDescription = form.textarea.data
        created_by = session['username']
        #create cursor
        cur= mysql.connection.cursor()

        #execute querry
        cur.execute('INSERT INTO businesses(title, owner, body) VALUES(%s, %s, %s)',(title, created_by, bDescription))

        #commit
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Your business has been registered, thank you!', 'success')
        return redirect(url_for('businesses'))
    else:
        return render_template('/forms/add_business.html',form=form)




if __name__ =='__main__':
    #secret key
    app.secret_key='mysecretkey'
    app.run(debug=True)