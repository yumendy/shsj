from django.contrib import admin
from volunteer.models import *

# Register your models here.
class ReportAdmin(admin.ModelAdmin):
	list_display = ('name', 'author', 'status')

admin.site.register(MyUser)
admin.site.register(Report,ReportAdmin)