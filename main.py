from flask import Flask,render_template,request,flash,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_bcrypt import Bcrypt




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Utilisation d'une base de données SQLite 
db = SQLAlchemy(app)
app.secret_key="main"

bcrypt = Bcrypt(app)


migrate = Migrate(app,db)

 # Equivalent en JEE d'un bean User

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


  # Equivalent en JEE d'un bean messages

class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(80), unique=False, nullable=False)
    destinataire = db.Column(db.String(80), unique=False, nullable=False)
    message = db.Column(db.String(800), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)




 #@app.route("/", methods=['GET', 'POST']) # Equivalent en JEE de @WebServlet
 #def accueil():
    



@app.route("/login", methods=['GET', 'POST']) # Equivalent en JEE de @WebServlet
def connection():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')


        # Vérifier si l'utilisateur existe et le couple username/password est valide
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            flash(f"Connexion réussie en tant que {username}")
            session['username'] = username
            
            return redirect(url_for('message'))
        else:
            flash("Identifiants incorrects. Veuillez réessayer.")
            return redirect(url_for('connection'))
    
    # Si la méthode n'est pas 'POST', simplement rediriger vers la page de connexion
    session.pop('_flashes', None)
    return render_template("connection.html")
    

@app.route('/bdd')
def show_database():
    users = User.query.all()
    messages=Messages.query.all()
    return render_template('database.html', users=users,messages=messages)




@app.route("/signup",methods=['GET','POST'])

def inscription():
    if request.method == "POST":
    	  # Equivalent en JEE de request.getParameter("username") et request.getParameter("passaword")

        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')


        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("inscription.html")
        else:
            # Créer un nouvel utilisateur
            new_user = User(username=username, password=hashed_password)

            # Ajouter l'utilisateur à la base de données
            db.session.add(new_user)
            db.session.commit()

            flash("Inscription réalisée")
            return render_template("connection.html")
    else:
        return render_template("inscription.html")



@app.route("/messages")
def message():
    # Récupérer le nom d'utilisateur depuis la session
    username = session.get('username', None)
    
    # Vérifier si le nom d'utilisateur est présent dans la session
    if username:
        # Récupérer la liste des utilisateurs depuis la base de données
        users = User.query.all()
        return render_template('message.html', username=username, users=users)
    else:
        # Rediriger vers la page de connexion si le nom d'utilisateur n'est pas présent
        flash("Veuillez vous connecter pour accéder à cette page.")
        return redirect(url_for('connection'))






@app.route('/chatbox', methods=['GET', 'POST'])
def chatbox():


    if request.method == 'POST':
        source = session.get('username', None)
        destinataire = request.form["selected_user"]

        messages = Messages.query.filter(
    ((Messages.source == source) & (Messages.destinataire == destinataire)) |
    ((Messages.source == destinataire) & (Messages.destinataire == source))
).all()

        return render_template('chatbox.html', messages=messages,source=source,destinataire=destinataire)
    else:
        users = User.query.all()
        username = session.get('username', None)

        return render_template('message.html', username=username, users=users)




@app.route('/addmessage', methods=['POST'])
def add_message():
    if request.method == 'POST':
        message_content = request.form.get('message')




        destinataire = request.form.get('destinataire')
        source = session.get('username', None)

        # Créer une nouvelle instance de la classe Messages
        new_message = Messages(source=source, destinataire=destinataire, message=message_content)

        # Ajouter le nouveau message à la session et le sauvegarder dans la base de données
        db.session.add(new_message)
        db.session.commit()

        messages = Messages.query.filter(
    ((Messages.source == source) & (Messages.destinataire == destinataire)) |
    ((Messages.source == destinataire) & (Messages.destinataire == source))
).all()
       

        # Vous pouvez également rediriger l'utilisateur vers une autre page après l'envoi du message
        return render_template('chatbox.html', messages=messages,source=source,destinataire=destinataire)

    # Gérez le cas où la méthode n'est pas POST (peut-être une redirection manuelle vers cette URL)
    else:
        return redirect(url_for('connection'))





     
     






# permet la création automatique de la BDD comme avec hibernate
with app.app_context():
    db.create_all()

if __name__ == "__main__":
      app.run(debug=True)
