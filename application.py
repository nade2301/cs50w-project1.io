from distutils.util import execute
import os
from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from flask import  request
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from flask import jsonify
from helpers import apology, login_required, lookup, usd
from sqlalchemy.sql.elements import Null





app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine=create_engine("postgresql://utwlkmktfogwgb:ac9ef83d5d42851bc003ef8d8f787fb60135ff60b4c01677d43fa24d89165b89@ec2-3-227-68-43.compute-1.amazonaws.com:5432/dd02qfvs718u21")
db=scoped_session(sessionmaker(bind=engine))



@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    
    ##isbn='080213825X'
    ##response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
    ##print(response)
    print("nada",session["user_id"])
    
    
    
    print({request.form.get('busqueda')})
    result= db.execute(f"SELECT isbn, title, author, year, id from books where upper(author)='{request.form.get('busqueda')}' or upper(author) LIKE upper('%{request.form.get('busqueda')}%') or upper(isbn)='{request.form.get('busqueda')}' or upper(isbn) LIKE upper('%{request.form.get('busqueda')}%') or upper(title)='{request.form.get('busqueda')}' or upper(title) LIKE upper('{request.form.get('busqueda')}') or upper(year)='{request.form.get('busqueda')}' or upper(year) LIKE upper('{request.form.get('busqueda')}') GROUP BY title, isbn, author, year, id ")
  
    print(result)

    return render_template("index.html", result=result)

@app.route("/resena/<id>", methods=["GET", "POST"])
@login_required
def resena(id):
    
    ##isbn='080213825X'
    ##response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
    ##print(response)
    
    
    
    
    if request.method=="POST":
        puntuacion=request.form.get("puntuacion")
        comentario=request.form.get("comentario")
        
        db.execute("INSERT INTO rev(book_id,comentario,puntuacion,user_id) VALUES (:id,:comentario,:puntuacion,:user_id)",{"id":id,"comentario":comentario,"puntuacion":puntuacion,"user_id":session['user_id']})
        db.commit()
        
    reviews=db.execute("SELECT  *from rev as r inner join users as u on r.user_id=u.id where book_id=:id",{"id":id})
    
    isbn=db.execute(f"SELECT isbn FROM books where id=:id",{"id":id}).fetchone()["isbn"]
    
    
    
    
    response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
  
    lib= db.execute(f"SELECT*from books where id=:id",{"id":id}).fetchone()
    
    if(response.get("totalItems")!=0):
        item=response.get("items")[0]
        
        volumeninfo=item.get("volumeInfo")
        
        image=volumeninfo.get("imageLinks")
        if not image:
            image=("holi")
        else: 
            image=image.get("thumbnail")
        print("lol",image)
    else:
        image=("holi")
        
    if(response.get("totalItems")!=0):
        item=response.get("items")[0]
        volumeninfo=item.get("volumeInfo")
        averagerating=volumeninfo.get("averageRating")
        ratingscount=volumeninfo.get("ratingsCount")
        print("mana",averagerating)
        print("mine",ratingscount)
    else:
        averagerating=0
        ratingscount=0
   
    comentario=db.execute("SELECT count (*) AS conteo FROM rev WHERE user_id=:user_id AND book_id=:id",{"user_id":session['user_id'],"id":id}).fetchone()["conteo"]
    print("bf",comentario)
    
    return render_template("resena.html",lib=lib,image=image,averagerating=averagerating,ratingscount=ratingscount,reviews=reviews,comentario=comentario)





    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        user = request.form.get("username")

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        ##rows = db.execute("SELECT * FROM users WHERE username = :user", {"user": user}).fetchall()
        
        count = 0
        hash = Null
        id = 0

        for rows in db.execute("SELECT count(username), hash, id FROM users WHERE username = :username GROUP BY username, id, hash",
                               {"username": request.form.get("username")}):
            count = rows[0]
            hash = rows['hash']
            id = rows['id']

        print(count)

        # Ensure username exists and password is correct
        if count == 0 or not check_password_hash(hash, request.form.get("password")):
            flash("nombre de usuario o contraseña inválido", "error")
            return render_template("login.html")

        # Ensure username exists and password is correct
        ##if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
           ## return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] =id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register use"""
    if request.method == "GET":
        return render_template("register.html")

    else:
        usuario = request.form.get("username")
        contrasena = request.form.get("password")
        confirmacion = request.form.get("confirmation")

        if not usuario:
            return apology("Rellene el campo de usuario")
        if not contrasena:
            return apology("Rellene el campo de contraseña")
        if not confirmacion:
            return apology("Rellene el campo de confirmacion")
        if contrasena != confirmacion:
            return apology("Contraseñas no coinciden")

        rows = db.execute("SELECT * FROM users WHERE username = :user", {"user": usuario}).fetchall()

        if not rows:
            hash= generate_password_hash(contrasena) 
            nuevo = db.execute("INSERT INTO users (username,hash) VALUES (:user, :hash) returning id", {"user": usuario, "hash": hash}).fetchone()
            db.commit()
        elif rows:
            return apology("El usuario ya existe.")
        session["user_id"] = nuevo
        return redirect("/")

    
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/api/<code>")
def api(code):
    response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+code).json()
    if(response.get("totalItems")!=0):
        item=response.get("items")[0]
        volumeninfo=item.get("volumeInfo")
        averagerating=volumeninfo.get("averageRating")
        ratingscount=volumeninfo.get("ratingsCount")
        title=volumeninfo.get("title")
        author=volumeninfo.get("authors")
        publishdate=volumeninfo.get("publishedDate")
        print("mana",averagerating)
        print("mine",ratingscount)
    else:
       return redirect("/error404")
        
    return jsonify(averagerating=averagerating,ratingscount=ratingscount,title=title,author=author,publishdate=publishdate)

@app.route("/error404")
def error():
    return render_template("404.html")