from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User,Permission
from django.core.validators import MaxValueValidator
#from .views import *
from django.urls import reverse

class Branch(models.Model):
	name=models.CharField(max_length=50)
	def __str__(self):
		return self.name

class Section(models.Model):
	name=models.CharField(max_length=50)
	def __str__(self):
		return self.name
		
class Hostel(models.Model):
	name=models.CharField(max_length=50)
	def __str__(self):
		return self.name

class Gender(models.Model):
	name=models.CharField(max_length=50)
	def __str__(self):
		return self.name

class Profile(models.Model):
	userid=models.ForeignKey(User)
	first_name=models.CharField(max_length=100,default='Please update your')
	last_name=models.CharField(max_length=100,default='Profile')
	branch=models.ForeignKey(Branch)
	section=models.ForeignKey(Section)
	year=models.PositiveIntegerField(default=0,validators=[MaxValueValidator(5),])
	birthdate=models.DateField('Date of Birth',default=timezone.now)
	hostel=models.ForeignKey(Hostel)
	room=models.PositiveIntegerField(default=0,validators=[MaxValueValidator(500),])
	emailid=models.EmailField()
	gender=models.ForeignKey(Gender,null=True)

	def __str__(self):
		return self.first_name+" "+self.last_name

class Election(models.Model):
	election_name=models.CharField(max_length=50)
	nom_start_time=models.DateTimeField('Nominations start time',default=timezone.now)
	nom_end_time=models.DateTimeField('Nominations end time',default=timezone.now)
	vote_start_time=models.DateTimeField('Voting start time',default=timezone.now)
	vote_end_time=models.DateTimeField('Voting end time',default=timezone.now)
	desc=models.TextField()
	def __str__(self):
		return self.election_name
	def nomval(self):
		if self.nom_start_time>timezone.now():
			return "1"
		elif self.nom_end_time>=timezone.now():
			return "2"
		else:
			return "3"
	def winner(self):
		x=self.candidate_set.all().order_by('-vote_count')
		if x:
			return x[0]
		else:
			return None
	def get_absolute_url(self):
		return reverse('index',kwargs={'slug':self.slug})

class Candidate(models.Model):
	myid=models.AutoField(primary_key=True)
	election=models.ForeignKey(Election,on_delete=models.CASCADE)
	name=models.CharField(max_length=50)
	branch=models.CharField(max_length=50)
	work_experience=models.TextField()
	user=models.CharField(max_length=30)
	vote_count=models.IntegerField(default=0)
	profile_pic=models.ImageField(upload_to='media/',blank=True)
	def __str__(self):
		return self.name

class Comment(models.Model):
	candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE)
	user=models.CharField(max_length=30)
	comment_content=models.CharField(max_length=3000)
	comment_time=models.DateTimeField('Comment Time')
	def __str__(self):
		return self.comment_content
	def isCandidate(self):
		return candidate.user==self.user

class Voter(models.Model):
	election=models.ForeignKey(Election,on_delete=models.CASCADE)
	user=models.CharField(max_length=30)
