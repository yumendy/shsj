from django.shortcuts import render, render_to_response
from django.template import Context, RequestContext
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User

# Create your views here.

def get_headimg(number):
	if number:
		pic = 'http://xscj.hit.edu.cn/hitjwgl/XS/XSZP/ZP'+number[:3]+'/'+number+'.jpg'
		return pic
	else:
		return ''

def homepage(req):
	username = req.session.get('username','')
	content = {'active_menu':'homepage'}
	if username != '':
		user = MyUser.objects.get(user__username = username)
		content['name'] = user.name
	else:
		content['name'] = ''
	return render_to_response('index.html',content)

def signup(req):
	if req.session.get('username',''):
		return HttpResponseRedirect('/')
	status = ''
	if req.POST:
		post = req.POST
		passwd = post.get('passwd','')
		repasswd = post.get('repasswd','')
		if passwd != repasswd:
			status = 're_err'
		else:
			if User.objects.filter(username = post.get('username','')):
				status = 'user_exist'
			else:
				newuser = User.objects.create_user( username = post.get('username',''), \
													password = post.get('passwd',''), \
													email = post.get('email',''), \
													)
				newuser.save()
				new_myuser = MyUser(user = newuser, \
									name = post.get('name',''), \
									num = post.get('num',''), \
									classnum = post.get('classnum',''), \
									permission = 1, \
									headImg = get_headimg(post.get('num',''))
									)
				new_myuser.save()
				status = 'success'
	content = {'active_menu':'homepage','status':status}
	return render_to_response('signup.html', content, context_instance = RequestContext(req))

def login(req):
	if req.session.get('username',''):
		return HttpResponseRedirect('/')
	status = ''
	if req.POST:
		post = req.POST
		username = post.get('username','')
		password = post.get('passwd','')
		user = auth.authenticate(username = username, password = password)
		if user is not None:
			if user.is_active:
				auth.login(req,user)
				req.session['username'] = username
				return HttpResponseRedirect('/')
			else:
				status = 'not_active'
		else:
			status = 'not_exist_or_passwd_err'
	content = {'active_menu':'homepage','status':status}
	return render_to_response('login.html', content, context_instance = RequestContext(req))