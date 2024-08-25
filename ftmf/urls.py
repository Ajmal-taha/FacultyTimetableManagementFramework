# urls.py
from django.urls import path, register_converter
from . import views
from .converters import BoolConverter

register_converter(BoolConverter, 'bool')

urlpatterns = [
    path('', views.home, name='timetable'),
    path('staff_timetable/', views.staff_timetable, name='staff_timetable'),
    path('staff_timetable/<int:staff_id>/', views.staff_timetable, name='staff_timetable'),
    path('section_timetable/', views.section_timetable, name='section_timetable'),
    path('section_timetable/<int:section_id>/', views.section_timetable, name='section_timetable'),
    path('staff_list/', views.staff_list, name='staff_list'),
    path('add_staff/', views.add_staff, name='add_staff'),
    path('delete_staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('add_subject/<int:staff_id>/', views.add_subject, name='add_subject'),
    path('remove_subject/', views.remove_subject, name='remove_subject'),
    path('display_all_data/', views.display_all_data, name='display_all_data'),
    path('add_section/<int:staff_id>/', views.add_section, name='add_section'),
    path('remove_section/<int:staff_id>/<int:section_id>/', views.remove_section, name='remove_section'),
    path('create_timetable_instance_from_staff_timetable/', views.create_timetable_instance_from_staff_timetable, name = 'create_timetable_instance_from_staff_timetable'),
    path('create_timetable_instance_from_section_timetable/', views.create_timetable_instance_from_section_timetable, name = 'create_timetable_instance_from_section_timetable'),
    path('delete_timetable_instance_from_staff_timetable/', views.delete_timetable_instance_from_staff_timetable, name = 'delete_timetable_instance_from_staff_timetable'),
    path('delete_timetable_instance_from_section_timetable/', views.delete_timetable_instance_from_section_timetable, name = 'delete_timetable_instance_from_section_timetable'),
    path('subject_list/', views.subject_list, name='subject_list'),
    path('section_list/', views.section_list, name='section_list'),
    path('delete_subject/', views.delete_subject, name='delete_subject'),
    path('delete_section/', views.delete_section, name='delete_section'),
    path('create_subject/',  views.create_subject, name='create_subject'),
    path('create_section/', views.create_section, name='create_section'),
    path('timetable/<str:name>/<int:_id>/', views.timetable_image_view, name='timetable_image'),
    path("master/", views.master_timetable, name = "master"),


    path('subs/', views.SubList.as_view()),
]