from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class MyUser(models.Model):
	name = models.CharField(max_length = 32)
	num = models.CharField(max_length = 11)
	classnum = models.CharField(max_length = 8)
	permission = models.IntegerField()
	headImg = models.URLField()

	user = models.OneToOneField(User)

	def __unicode__(self):
		return self.name

class Report(models.Model):
	name = models.CharField(max_length = 128)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	submit_time = models.DateTimeField(auto_now=True)
	apply_time = models.FloatField()
	address = models.CharField(max_length = 128)
	info = models.TextField(max_length = 20480)
	status = models.IntegerField()
	report_type = models.IntegerField()
	author_type = models.IntegerField()
	info_type = models.IntegerField()
	img1 = models.URLField(null=True)
	img2 = models.URLField(null=True)

	author = models.ForeignKey(MyUser)
	checker = models.CharField(max_length = 32,null=True)

	def __unicode__(self):
		return self.author.name + '<<' + self.name + '>>'