from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import widgets

from .models import Election,Profile,Branch,Section,Hostel

class ElectionForm(forms.ModelForm):
	class Meta:
		model = Election
		fields = ['election_name','nom_start_time','nom_end_time','vote_start_time','vote_end_time','desc']	

class EditProfileForm(forms.ModelForm):
	class Meta(object):
		model = Profile
		fields = ['first_name','last_name','gender','branch','section','year','birthdate','hostel','room','emailid']

