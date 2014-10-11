from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class MyUser(models.Model):
	name = models.CharField(max_length = 32)
	num = models.CharField(max_length = 11)
	classnum = models.CharField(max_length = 8)
	permission = models.IntegerField()
	headIng = models.URLField()

	user = models.OneToOneField(User)

	def __unicode__(self):
		return self.name

class Report(models.Model):
	name = models.CharField(max_length = 128)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	apply_time = models.FloatField()
	address = models.CharField(max_length = 128)
	info = models.TextField(max_length = 20480)
	status = models.IntegerField()
	author_type = models.IntegerField()
	img1 = models.URLField()
	img2 = models.URLField()

	author = models.ForeignKey(MyUser)

	def __unicode__(self):
		return self.author.name + '<<' + self.name + '>>'