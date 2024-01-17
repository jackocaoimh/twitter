from flask import Flask, render_template, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy 
from models import User, connect_db, db, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from werkzeug.exceptions import Unauthorized

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
    def register():
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
    
    # Route for adding new feedback to users account
    @app.route('/user/<username>/feedback/new', methods=['GET', 'POST'])
    def new_feedback(username):

        if "username" not in session or username != session['username']:
            raise Unauthorized()
        
        user = User.query.filter_by(username=username).first()

        form = FeedbackForm()

        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            feedback = Feedback(
                title = title,
                content = content,
                username =username,
            )

            db.session.add(feedback)
            db.session.commit()

            return redirect(f'/user/{user.username}')

        else:
            return render_template('feedback_form.html', form=form)


    @app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
    def delete_feedback(feedback_id):
    
        feedback = Feedback.query.get_or_404(feedback_id)
        if feedback.username != session['username']:
            raise Unauthorized("User not authorized to delete this feedback")

        db.session.delete(feedback)
        db.session.commit()

        return redirect(url_for('secret', username=session['username']))
    
    @app.route('/feedback/<int:feedback_id>/edit', methods=['GET', 'POST'])
    def edit_feedback(feedback_id):
    
        feedback = Feedback.query.get_or_404(feedback_id)
        if feedback.username != session['username']:
            raise Unauthorized("User not authorized to delete this feedback")

        form = FeedbackForm(obj=feedback)

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data

            db.session.commit()

            return redirect(url_for('secret', username=session['username']))
        
        return render_template('feedback_edit.html', form=form, feedback=feedback)
    
    @app.route('/user/<username>/delete', methods=['POST'])
    def delete_user(username):
        
        if "username" not in session or username != session['username']:
            raise Unauthorized()
        
            user = User.query.get(username)
            db.session.delete(user)
            db.session.commit()
            session.pop('username')

        return redirect('/register')

    
   
