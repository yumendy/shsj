from django.shortcuts import render, render_to_response
from django.template import Context, RequestContext
from models import *
import re
import datetime
from markdown import markdown
from random import randint
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User

from sae.storage import Bucket, Client
from sae.ext.storage import monkey
monkey.patch_all()

# Create your views here.

def get_headimg(number):
	if number:
		pic = 'http://xscj.hit.edu.cn/hitjwgl/XS/XSZP/ZP'+number[:3]+'/'+number+'.jpg'
		return pic
	else:
		return ''

def num_need_check():
	check_lst = Report.objects.filter(status = 1)
	return len(check_lst)

def homepage(req):
	username = req.session.get('username','')
	content = {'active_menu':'homepage','num_need_check':num_need_check()}
	if username != '':
		user = MyUser.objects.get(user__username = username)
		content['user'] = user
	else:
		content['user'] = ''
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
		elif len(post.get('classnum','')) != 8:
			status = 'classnum_err'
		else:
			if User.objects.filter(username = post.get('username','')):
				status = 'user_exist'
			elif MyUser.objects.filter(num = post.get('num','')):
				status = 'num_exist'
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
	content = {'active_menu':'homepage','status':status,'num_need_check':num_need_check(),'user':''}
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
	content = {'active_menu':'homepage','status':status,'num_need_check':num_need_check(),'user':''}
	return render_to_response('login.html', content, context_instance = RequestContext(req))

def logout(req):
	auth.logout(req)
	return HttpResponseRedirect('/')

def submit_report(req):
	username = req.session.get('username','')
	content = {'active_menu':'submitReport','num_need_check':num_need_check()}
	status = ''
	if username != '':
		user = MyUser.objects.get(user__username = username)
		content['user'] = user
	else:
		return HttpResponseRedirect('/login/')
	if req.POST:
		post = req.POST
		if req.FILES:
			img1 = req.FILES['img1']
			img2 = req.FILES['img2']
			bucket = Bucket('img')
			bucket.put()
			bucket.post(acl='.r:.sinaapp.com,.r:sae.sina.com.cn')
			tut1 = img1._name.split('.')[-1]
			tut2 = img2._name.split('.')[-1]
			if tut1.lower() not in ['jpg','jpeg','bmp','gif','png']:
				tut1 = 'jpg'
			if tut2.lower() not in ['jpg','jpeg','bmp','gif','png']:
				tut2 = 'jpg'
			dt_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d%H%M%S')
			filename1 = dt_str + str(randint(100,999)) + '.' + tut1
			filename2 = dt_str + str(randint(100,999)) + '.' + tut2
			bucket.put_object(filename1,img1)
			bucket.put_object(filename2,img2)
		info = post.get('info','')
		if len(info) < 500:
			status = 'info_short'
		else:
			report = Report(
							name = post.get('name',''),
							start_time = post.get('start_time',''),
							end_time = post.get('end_time',''),
							address = post.get('address',''),
							status = 1,
							apply_time = 0,
							apply_score = 0,
							report_type = post.get('report_type',''),
							author_type = post.get('author_type',''),
							info_type = post.get('info_type',''),
							author = user,
							img1 = bucket.generate_url(filename1), \
							img2 = bucket.generate_url(filename2), \
							)
			if post.get('info_type','') == '2':
				a = re.compile(r'(<script)(.*)(>)',re.I)
				res = r'&lt;script\2&gt;'
				report.info = a.sub(res,info)
			else:
				report.info = info
			report.save()
			status = 'success'
		content['status'] = status
	return render_to_response('submitreport.html', content, context_instance = RequestContext(req))

def report_list(req):
	username = req.session.get('username','')
	if username != '':
		user = MyUser.objects.get(user__username = username)
	else:
		return HttpResponseRedirect('/login/')
	report_list = Report.objects.filter(author = user).order_by('-submit_time')
	# TODO: Add some info about report list and score
	content = {'active_menu':'checkReport','num_need_check':num_need_check(),'user':user,'report_list':report_list}
	return render_to_response('report_list.html',content)

def report_edit(req):
	username = req.session.get('username','')
	status = ''
	if username != '':
		user = MyUser.objects.get(user__username = username)
	else:
		return HttpResponseRedirect('/login/')
	Id = req.GET.get('id','')
	try:
		report = Report.objects.get(pk = Id)
	except:
		return HttpResponseRedirect('/reportlist/')
	if report.author != user:
		return HttpResponseRedirect('/reportlist/')
	else:
		if report.status != 1:
			status = 'cannot_edit'
		else:
			if req.POST:
				post = req.POST
				if req.FILES:
					img1 = req.FILES['img1']
					img2 = req.FILES['img2']
					bucket = Bucket('img')
					bucket.put()
					bucket.post(acl='.r:.sinaapp.com,.r:sae.sina.com.cn')
					tut1 = img1._name.split('.')[-1]
					tut2 = img2._name.split('.')[-1]
					if tut1.lower() not in ['jpg','jpeg','bmp','gif','png']:
						tut1 = 'jpg'
					if tut2.lower() not in ['jpg','jpeg','bmp','gif','png']:
						tut2 = 'jpg'
					dt_str = datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d%H%M%S')
					filename1 = dt_str + str(randint(100,999)) + '.' + tut1
					filename2 = dt_str + str(randint(100,999)) + '.' + tut2
					bucket.put_object(filename1,img1)
					bucket.put_object(filename2,img2)
				info = post.get('info','')
				if len(info) < 500:
					status = 'info_short'
				else:
					report.name = post.get('name','')
					report.start_time = post.get('start_time','')
					report.end_time = post.get('end_time','')
					report.address = post.get('address','')
					report.report_type = post.get('report_type','')
					report.author_type = post.get('author_type','')
					report.info_type = post.get('info_type','')
					try:
						img1 = bucket.generate_url(filename1)
						img2 = bucket.generate_url(filename2)
						report.img1 = img1
						report.img2 = img2
					except:
						pass
					if post.get('info_type','') == '2':
						a = re.compile(r'(<script)(.*)(>)',re.I)
						res = r'&lt;script\2&gt;'
						report.info = a.sub(res,info)
					else:
						report.info = info
					report.save()
					status = 'success'
	content = {'user':user,'active_menu':'submitReport','num_need_check':num_need_check(),'report':report, 'status':status}
	return render_to_response("report_edit.html",content,context_instance = RequestContext(req))

def report_detail(req):
	username = req.session.get('username','')
	if username != '':
		user = MyUser.objects.get(user__username = username)
	else:
		return HttpResponseRedirect('/login/')
	Id = req.GET.get('id','')
	try:
		report = Report.objects.get(pk = Id)
	except:
		if user.permission == 1:
			return HttpResponseRedirect('/reportlist/')
		elif user.permission > 1 and num_need_check() > 0:
			return HttpResponseRedirect('/auditinglist/')
		else:
			return HttpResponseRedirect('/')
	if user.permission == 1:
		if report.author != user:
			return HttpResponseRedirect('/reportlist/')
	if report.info_type == 2:
		report.info = markdown(report.info)
	content = {'report':report,'user':user,'num_need_check':num_need_check(),'active_menu':'checkReport'}
	return render_to_response('report.html',content)

def auditing_list(req):
	username = req.session.get('username','')
	if username != '':
		user = MyUser.objects.get(user__username = username)
	else:
		return HttpResponseRedirect('/login/')
	if user.permission == 1:
		return HttpResponseRedirect('/')
	else:
		auditing_list = Report.objects.filter(status = 1)
	content = {'auditing_list':auditing_list,'user':user,'num_need_check':num_need_check(),'active_menu':'auditingReport'}
	return render_to_response('auditing_list.html',content)

def report_auditing(req):
	username = req.session.get('username','')
	if username != '':
		user = MyUser.objects.get(user__username = username)
	else:
		return HttpResponseRedirect('/login/')
	if user.permission == 1:
		return HttpResponseRedirect('/')
	else:
		Id = req.GET.get('id','')
		try:
			report = Report.objects.get(pk = Id)
		except:
			if user.permission > 1 and num_need_check() > 0:
				return HttpResponseRedirect('/auditinglist/')
			else:
				return HttpResponseRedirect('/')
	if req.POST:
		post = req.POST
		status = post.get('status',1)
		report.status = status
		if status == '2':
			report.apply_score = post.get('apply_score',0)
			report.apply_time = post.get('apply_time',0)
		report.checker = user.name
		report.save()
		url = '/reportlist/detail/?id=' + str(report.id)
		return HttpResponseRedirect(url)
	if report.info_type == 2:
		report.info = markdown(report.info)
	content = {'user':user,'num_need_check':num_need_check(),'active_menu':'auditingReport','report':report}
	return render_to_response('report_auditing.html',content,context_instance = RequestContext(req))

def querry(req):
	username = req.session.get('username','')
	if username != '':
		user = MyUser.objects.get(user__username = username)
	else:
		return HttpResponseRedirect('/login/')
	if user.permission < 3:
		return HttpResponseRedirect('/')
	else:
		if req.POST:
			post = req.POST
			model = post.get('model','')
			key = post.get('key','')
			st_time = post.get('st_time','')
			ed_time = post.get('ed_time','')
			status = ''
			if model == '1':
				try:
					student = MyUser.objects.get(num = key)
				except:
					status = 'no_student'
				else:
					reportlist = Report.objects.filter(author__num = key).filter(submit_time__gte = st_time).filter(submit_time__lte = ed_time)
					sum_report = len(reportlist)
					score = 0
					for item in reportlist:
						score += item.apply_time * item.apply_score
					st_time = datetime.datetime.strptime(st_time,'%Y-%m-%dT%H:%M')
					ed_time = datetime.datetime.strptime(ed_time,'%Y-%m-%dT%H:%M')
				content = {'model':model,'reportlist':reportlist,'sum_report':sum_report,'score':score,'user':user,'num_need_check':num_need_check(),'active_menu':'queryReport','student':student,'key':key,'st_time':st_time,'ed_time':ed_time}
			elif model == '2':
				reportlist = Report.objects.filter(author__name = key).filter(submit_time__gte = st_time).filter(submit_time__lte = ed_time)
				st_time = datetime.datetime.strptime(st_time,'%Y-%m-%dT%H:%M')
				ed_time = datetime.datetime.strptime(ed_time,'%Y-%m-%dT%H:%M')
				content = {'model':model,'reportlist':reportlist,'user':user,'num_need_check':num_need_check(),'active_menu':'queryReport','key':key,'st_time':st_time,'ed_time':ed_time}
			elif model == '3':
				reportlist = Report.objects.filter(author__classnum = key).filter(submit_time__gte = st_time).filter(submit_time__lte = ed_time)
				sum_report = len(reportlist)
				score = 0
				for item in reportlist:
					score += item.apply_time * item.apply_score
				st_time = datetime.datetime.strptime(st_time,'%Y-%m-%dT%H:%M')
				ed_time = datetime.datetime.strptime(ed_time,'%Y-%m-%dT%H:%M')
				content = {'model':model,'reportlist':reportlist,'sum_report':sum_report,'score':score,'user':user,'num_need_check':num_need_check(),'active_menu':'queryReport','key':key,'st_time':st_time,'ed_time':ed_time}
			elif model == '4':
				reportlist = Report.objects.all().filter(submit_time__gte = st_time).filter(submit_time__lte = ed_time)
				sum_report = len(reportlist)
				score = 0
				for item in reportlist:
					score += item.apply_time * item.apply_score
				st_time = datetime.datetime.strptime(st_time,'%Y-%m-%dT%H:%M')
				ed_time = datetime.datetime.strptime(ed_time,'%Y-%m-%dT%H:%M')
				content = {'model':model,'reportlist':reportlist,'sum_report':sum_report,'score':score,'user':user,'num_need_check':num_need_check(),'active_menu':'queryReport','st_time':st_time,'ed_time':ed_time}
			return render_to_response('result.html',content)
		else:
			content = {'user':user,'num_need_check':num_need_check(),'active_menu':'queryReport'}
			return render_to_response('querry.html',content,context_instance = RequestContext(req))

def setpasswd(req):
	username = req.session.get('username','')
	if username != '':
		user = MyUser.objects.get(user__username = username)
	else:
		return HttpResponseRedirect('/login/')
	status = ''
	if req.POST:
		post = req.POST
		if user.user.check_password(post.get('old','')):
			if post.get('new','') == post.get('new_re',''):
				user.user.set_password(post.get('new',''))
				user.user.save()
				status = 'success'
			else:
				status = 're_err'
		else:
			status = 'passwd_err'
	content = {'user':user,'num_need_check':num_need_check(),'active_menu':'homepage','status':status}
	return render_to_response('setpasswd.html',content,context_instance = RequestContext(req))