# models.py
from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=100)
    year = models.CharField(max_length=10, default='1')
    semester = models.CharField(max_length=10, default='1')
    def __str__(self):
        return self.year+self.semester+self.name

class Staff(models.Model):
    name = models.CharField(max_length=100)
    subjects = models.ManyToManyField(Subject)
    sections = models.ManyToManyField(Section)

    def add_subject(self, subject_name):
        subject, created = Subject.objects.get_or_create(name=subject_name)
        self.subjects.add(subject)

    def remove_subject(self, subject_id):
        self.subjects.remove(subject_id)

    def add_section(self, section_name):
        section, created = Section.objects.get_or_create(name=section_name)
        self.sections.add(section)

    def remove_section(self, section_id):
        self.sections.remove(section_id)

    def __str__(self):
        return self.name+str(self.id)

    @classmethod
    def add_staff(cls, name):
        return cls.objects.create(name=name)

    @classmethod
    def delete_staff(cls, staff_id):
        staff = cls.objects.get(id=staff_id)
        staff.subjects.clear()  # Automatically removes all links to subjects
        staff.delete()

class Timetable(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day = models.CharField(max_length=100)  # e.g., Monday, Tuesday, etc.
    time_slot = models.IntegerField()  # Serial number representing the time slot, 0 represents first half time slot i.e. from 8:30 to 9:00
    availability = models.IntegerField()

class Images(models.Model):
    name = models.CharField(max_length=50)
    hotel_Main_Img = models.ImageField(upload_to='images/')