from django.contrib import admin

# Register your models here.
from .models import Staff, Subject, Section, Timetable

admin.site.register(Staff)
admin.site.register(Subject)
admin.site.register(Section)
admin.site.register(Timetable)