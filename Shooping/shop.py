from flask import *
from flask_sqlalchemy import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
class Users(db.Model):
	__tablename__='users'
	userId = db.Column(db.Integer,primary_key=True)
	password = db.Column(db.String(255))
	email = db.Column(db.String(255))
	name = db.Column(db.String(255))
	address = db.Column(db.String(255))
	state = db.Column(db.String(255))
	phone = db.Column(db.String(255))

	def __init__(self,userId,password,email,name,address,state,phone):
		self.userId=userId
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
	id = db.Column(db.Integer,primary_key=True)
	userId = db.Column(db.Integer,db.ForeignKey('users.userId'))
	productId = db.Column(db.String(255),db.ForeignKey('products.productId'))
	def __init__(self,userId,productId):
		self.userId=userId
		self.productId=productId
db.create_all()

	books = open('F:\msit\web technologies\Flaskr\Shooping\static\\books.json')
	data=books.read()
	jsondata=json.loads(data)
	result = jsondata['items']
	for i in range(len(result)):
		productId = result[i]['id']
		name = result[i]['volumeInfo']['title']
		image = result[i]['volumeInfo']['imageLinks']['thumbnail']
		if 'listPrice' in result[i]['saleInfo']:
			price = result[i]['saleInfo']['listPrice']['amount']
		else:
			price = 0.0
		description = str("Description: "+result[i]['volumeInfo']['description'])
		# print(productId+"\n"+name+"\n"+str(price)+"\n"+description)
		# print(description)
		author=str("Authors: "+','.join(map(str,result[i]['volumeInfo']['authors'])))
		publisher = str("Publishers: "+result[i]['volumeInfo']['publisher'])
		publishedDate= str("Published Data: "+result[i]['volumeInfo']['publishedDate'])
		new_ex =  Products(productId,name,price,description,image,author,publisher,publishedDate)
		db.session.add(new_ex)
	db.session.commit()