
from django.shortcuts import render
from django.http import HttpResponseRedirect
class GETEP:
	def __init__(self,get_response):
		self.get_response=get_response
	def __call__(self, request):
		a=self.get_response(request)
		if (a.status_code!=404):
			return a
		else:
			return render(request,'Election_Portal/notfnd.html',{})
