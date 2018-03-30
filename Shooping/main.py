from flask import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key="random string"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

class Users(db.Model):
	__tablename__='users'
	id = db.Column(db.Integer,primary_key=True)
	password = db.Column(db.String(255))
	email = db.Column(db.String(255))
	name = db.Column(db.String(255))
	address = db.Column(db.String(255))
	state = db.Column(db.String(255))
	phone = db.Column(db.String(255))

	def __init__(self,password,email,name,address,state,phone):
		# self.userId=userId
		self.password=password
		self.email=email
		self.name=name
		self.address=address
		self.state=state
		self.phone=phone
db.create_all()

class Products(db.Model):
	__tablename__='products'
	productId = db.Column(db.String(255),primary_key=True)
	name = db.Column(db.String(255))
	price = db.Column(db.Float)
	description = db.Column(db.String(4294000000))
	image = db.Column(db.String(429400000000))
	author = db.Column(db.String(255))
	publisher = db.Column(db.String(255))
	publishedDate=db.Column(db.String(255))

	def __init__(self,productId,name,price,description,image,author,publisher,publishedDate):
		self.productId=productId
		self.name=name
		self.price=price
		self.description=description
		self.image=image
		self.author = author
		self.publisher=publisher
		self.publishedDate=publishedDate

db.create_all()

class Kart(db.Model):
	__tablename__='kart'
	id = db.Column(db.Integer(),primary_key=True)
	email = db.Column(db.String(255),db.ForeignKey('users.email'))
	productId = db.Column(db.String(255),db.ForeignKey('products.productId'))
	quantity = db.Column(db.Integer())
	def __init__(self,email,productId,quantity):
		self.email = email
		self.productId = productId
		self.quantity = quantity
db.create_all()

class Orders(db.Model):
	__tablename__='orders'
	id = db.Column(db.Integer(),primary_key=True)
	email = db.Column(db.String(255),db.ForeignKey('users.email'))
	productId = db.Column(db.String(255),db.ForeignKey('products.productId'))
	quantity = db.Column(db.Integer())
	def __init__(self,email,productId,quantity):
		self.email = email
		self.productId = productId
		self.quantity = quantity
db.create_all()

def getLoginDetails():
	if 'email' not in session:
		loggedIn = False
		name = ''
		noOfItems = 0
	else:
		loggedIn = True
		stmt = "select email,name from users where email='"+session['email']+"'"
		userId, name = db.engine.execute(stmt).fetchone()
		stmt1 = "select count(productId) from kart where email = '" +str(userId) +"'"
		noOfItems = db.engine.execute(stmt1).fetchone()[0]
	return (loggedIn,name,noOfItems)

@app.route("/")
def root():
	loggedIn, name ,noOfItems = getLoginDetails()
	stmt="SELECT * FROM products"
	itemData = db.engine.execute(stmt).fetchall()
	return render_template('home.html',itemData=itemData,loggedIn=loggedIn,name=name,noOfItems=noOfItems)

# @app.route("/account/profile")
# def profileHome():
# 	if 'email' not in session:
# 		return redirect(url_for('root'))
# 	loggedIn,name,noOfItems = getLoginDetails()
# 	return render_template("profileHome.html",loggedIn=loggedIn,name=name,noOfItems=noOfItems)
@app.route("/loginForm")
def loginForm():
	if 'email' in session:
		return redirect(url_for('root'))
	else:
		return render_template('login.html',error='')
@app.route("/login", methods = ['POST','GET'])
def login():
	if request.method =='POST':
		email = request.form['email']
		password = request.form['password']
		if is_valid(email,password):
			session['email']=email
			return redirect(url_for('root'))
		else:
			error = 'Invalid UserId / password'
			return render_template('login.html',error=error)
@app.route("/productDescription")
def productDescription():
	loggedIn,name,noOfItems = getLoginDetails()
	productId = request.args.get('productId')
	stmt = 'SELECT productId,name,price,description,image,author,publisher,publishedDate FROM products WHERE productId = "'+str(productId)+'"'
	# print(productId)
	productData = db.engine.execute(stmt).fetchone()
	return render_template("productDescription.html",data=productData,loggedIn=loggedIn,name=name,noOfItems=noOfItems)
@app.route("/addToCart")
def addToCart():
	if 'email' not in session:
		return redirect(url_for('loginForm'))
	else:
		productId = str(request.args.get('productId'))
		stmt = "SELECT email FROM users WHERE email = '" + session['email'] + "'"
		email = db.engine.execute(stmt).fetchone()[0]
		# stmt = 'SELECT count() FROM kart'
		try:
			count = db.engine.execute("SELECT quantity FROM kart WHERE email = '" + email +"'AND productId ='"+str(productId)+"'").fetchone()[0]
			count+=1
			# print("count--> "+str(count))
			if(count <= 3):
				try:
					db.engine.execute("DELETE FROM kart WHERE email = '" + email + "' AND productId = '" + str(productId) +"'")
					db.session.commit()
					# print("asdfghjasdfgh")
					# print("after delete count--> "+str(count))
					user = Kart(email,productId,count+1)
					db.session.add(user)
					# print("after update count--> "+str(count))
					# print("123456789")
					db.session.commit()
					msg="Added successfully"
				except:
					db.session.rollback()
					msg = "Can't add more than 3 books"
		except:
			quantity=1
			user = Kart(email,productId,quantity)
			# print("qwertyuiop")
			db.session.add(user)
			db.session.commit()
			msg="Added successfully"
	db.session.close()
	return redirect(url_for('root'))
@app.route("/cart")
def cart():
	if 'email' not in session:
		return redirect(url_for('loginForm'))
	loggedIn,name,noOfItems = getLoginDetails()
	email = session['email']
	stmt = "SELECT email FROM users WHERE email = '" + str(session['email']) + "'"
	email = db.engine.execute(stmt).fetchone()[0]
	stmt1 = 'SELECT products.productId, products.name, products.price, products.image, kart.quantity FROM products, kart WHERE products.productId = kart.productId AND kart.email = "' + session['email'] +'"'
	products = db.engine.execute(stmt1).fetchall()
	totalPrice = 0
	for row in products:
		totalPrice+=row[2]*(row[4]-1)
	return render_template("cart.html",products=products,totalPrice=totalPrice,loggedIn=loggedIn,name=name,noOfItems=noOfItems)

@app.route("/orders")
def orders():
	if 'email' not in session:
		return redirect(url_for('loginForm'))
	loggedIn,name,noOfItems = getLoginDetails()
	email = session['email']
	stmt = "SELECT email FROM users WHERE email = '" + session['email'] + "'"
	email = db.engine.execute(stmt).fetchone()[0]
	stmt1 = 'SELECT products.productId, products.name, products.price, products.image, kart.quantity FROM products, kart WHERE products.productId = kart.productId AND kart.email = "' + session['email'] +'"'
	products = db.engine.execute(stmt1).fetchall()
	totalPrice = 0
	for row in products:
		totalPrice+=row[2]*(row[4]-1)
	return render_template("orders.html",products=products,totalPrice=totalPrice,loggedIn=loggedIn,name=name,noOfItems=noOfItems)

@app.route("/checkout")
def checkout():
	if 'email' not in session:
		return redirect(url_for('loginForm'))
	loggedIn,name,noOfItems = getLoginDetails()
	email = session['email']
	stmt = "SELECT email FROM users WHERE email = '" + str(session['email']) + "'"
	email = db.engine.execute(stmt).fetchone()[0]
	stmt1 = 'SELECT products.productId, products.name, products.price, products.image, kart.quantity FROM products, kart WHERE products.productId = kart.productId AND kart.email = "' + session['email'] +'"'
	products = db.engine.execute(stmt1).fetchall()
	totalPrice = 0
	for row in products:
		totalPrice+=row[2]*(row[4]-1)
	return render_template("checkout.html",products=products,totalPrice=totalPrice,loggedIn=loggedIn,name=name,noOfItems=noOfItems)
@app.route("/removeFromCart")
def removeFromCart():
	if 'email' not in session:
		return redirect(url_for('loginForm'))
	email = session['email']
	productId = str(request.args.get('productId'))
	stmt = "SELECT email FROM users WHERE email = '" + str(session['email']) + "'"
	email = db.engine.execute(stmt).fetchone()[0]
	try:
		stmt2 = 'DELETE FROM kart WHERE email = "' + str(session['email']) + '" AND productId = "' + str(productId) + '"'
		db.engine.execute(stmt2)
		db.session.commit()
		db.session.close()
		msg = "removed successfully"
	except:
		db.session.rollback()
		msg = "error occured"
		db.session.close()
	return redirect(url_for('root'))
@app.route("/logout")
def logout():
	session.pop('email',None)
	return redirect(url_for('root'))
def is_valid(email,password):
	stmt = "SELECT email, password FROM users"
	data = db.engine.execute(stmt).fetchall()
	for row in data:
		if row[0] == email and row[1] == password:
			return True
	return False

@app.route("/register",methods = ['GET','POST'])
def register():
	if request.method =='POST':
		password = request.form['password']
		email = request.form['email']
		name = request.form['name']
		address = request.form['address']
		state = request.form['state']
		phone = request.form['phone']
		try:
			user = Users(password,email,name,address,state,phone)
			db.session.add(user)
			db.session.commit()
			msg="registered successfully"
		except:
			db.session.rollback()
			msg="error ocuured"
	db.session.close()
	return render_template("login.html",error=msg)

@app.route("/registerationForm")
def registrationForm():
	return render_template("register.html")

if __name__ =='__main__':
	
	app.run(debug=True)
