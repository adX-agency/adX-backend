from django.shortcuts import render
from django.http import HttpResponse
import pyrebase
from django.contrib import auth
config = {
  "apiKey": "AIzaSyC8SpE7w0Zisz5-NhRwNoMNfiY36cpMAVQ",
  "authDomain": "wisper-1773e.firebaseapp.com",
  "databaseURL": "https://wisper-1773e.firebaseio.com",
  "storageBucket": "wisper-1773e.appspot.com",
  "messagingSenderId": "325348010767"
}

firebase = pyrebase.initialize_app(config)
database=firebase.database()
storage=firebase.storage()
authen = firebase.auth()

def index(request):
	return render(request,'adx/index.html')

def about(request):
	return render(request,'adx/about.html')

def signIn(request):
	return render(request, "adx/signIn.html")

def post_signin(request):
	email=request.POST.get('email')
	passw = request.POST.get("pass")
	try:
		user = authen.sign_in_with_email_and_password(email,passw)
		session_id=user['idToken']
		request.session['uid']=str(session_id)
	except:
		message="invalid credentials"
		return render(request,"adx/signIn.html",{"messg":message})
	ad_list = []
	vendorID = email
	vendorID = vendorID.replace('@', '')
	vendorID = vendorID.replace('.', '')
	user_ads_keys = database.child("users").child(vendorID).child("ads").get()
	try:
		for ad in user_ads_keys.each():
			ad_list.append(database.child('ads').child(ad.val()).get().val())
	except:
		ad_list = []
	name = database.child("users").child(vendorID).child('details').child('name').get().val()
	status = database.child("users").child(vendorID).child('details').child('status').get().val()
	return render(request,'adx/index.html', {'context': ad_list, 'name': name, 'status': status})

def signup(request):
	return render(request, "adx/signup.html")

def postsignup(request):
	name=request.POST.get('name')
	email=request.POST.get('email')
	passw=request.POST.get('pass')
	vendor=request.POST.get('vendor')
	ID = email.replace('@', '')
	ID = ID.replace('.', '')
	try:
		user=authen.create_user_with_email_and_password(email,passw)
	except:
		message="Unable to create account try again"
		return render(request,"adx/signup.html",{"messg":message})
	data={"name":name,"status":vendor}
	database.child("users").child(ID).child("details").set(data)
	return render(request,"adx/signIn.html")

def create(request):
	return render(request,'adx/create.html')

from werkzeug.utils import secure_filename

def post_create(request):
	title = request.POST.get('title')
	longitude = request.POST.get('longitude')
	latitude = request.POST.get('latitude')
	startdate = request.POST.get('startdate')
	enddate = request.POST.get('enddate')
	idtoken= request.session['uid']
	file = request.FILES['file']
	a = authen.get_account_info(idtoken)
	a = a['users']
	a = a[0]
	vendorID = a['email']
	vendorID = vendorID.replace('@', '')
	vendorID = vendorID.replace('.', '')
	adID = str(longitude) + str(latitude) + str(startdate) + str(enddate)
	adID = adID.replace('/', '')
	adID = adID.replace('.', '')
	data = {
	"title":title,
	'longitude':longitude,
	'latitude' :latitude,
	'startdate' :startdate,
	'enddate' : enddate,
	'vendorID' : vendorID,
	'adID': adID,
	'address': storage.child("ads").child(vendorID).child(adID).get_url(None),
	}
	ad_list = []
	if(longitude==None):
		print('no long')
	else:
		database.child('ads').child(adID).set(data)
		database.child('users').child(vendorID).child('ads').child(adID).set(adID)
		storage.child("ads").child(vendorID).child(adID).put(file)
	user_ads_keys = database.child("users").child(vendorID).child("ads").get()
	for ad in user_ads_keys.each():
		ad_list.append(database.child('ads').child(ad.val()).get().val())
	name = database.child("users").child(vendorID).child('details').child('name').get().val()
	status = database.child("users").child(vendorID).child('details').child('status').get().val()
	return render(request,'adx/index.html', {'context': ad_list, 'name': name, 'status': status})

def log_out(request):
	auth.logout(request)
	return render(request,'adx/signIn.html')