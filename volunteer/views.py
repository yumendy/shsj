from django.shortcuts import render, render_to_response
from django.template import Context, RequestContext
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User

# Create your views here.
def homepage(req):
	username = req.session.get('username','')
	content = {}
	if username != '':
		user = MyUser.objects.get(user__username = username)
		content['name'] = user.name
	else:
		content['name'] = ''
	return render_to_response('index.html',content)