from flask import Flask, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy 
from models import User, connect_db, db
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://jackocaoimh:turner12345@localhost/twitter"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
with app.app_context():
    db.create_all()

    @app.route('/')
    def root():
        return redirect('/register')
    
    @app.route('/register', methods=["GET", "POST"])
    def register(username):
        form = RegisterForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data
            first_name = form.first_name.data
            last_name = form.last_name.data

            user = User.register(username, password, email, first_name, last_name)
            db.session.add(user)
            db.session.commit()

            session['username'] = user.username

            return redirect(f'/user/{user.username}')
        
        else:
            return render_template('register.html', form = form )
        
    @app.route('/user/<username>')
    def secret(username):
        if "username" not in session:
            flash("You must be logged in to view!")
            return redirect("/login")

        else:
            user = User.query.get_or_404(username)
            return render_template("user_info.html", username=username, user=user)
        
    
    @app.route('/login', methods=["POST", "GET"])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = User.authenticate(username, password)

            if user:
                session['username'] = user.username
                return redirect(f'/user/{user.username}')
            
            else:
                form.username.errors = ['Invalid username/password.']
        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        
        session.pop('username')

        return redirect('/login')