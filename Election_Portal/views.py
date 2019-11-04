from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse
import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Election,Comment,Candidate,Voter,Branch,Section,Hostel,Profile
from django.db import transaction
from django.core.mail import EmailMessage,send_mail
from .forms import ElectionForm,EditProfileForm
from django.contrib.auth.models import User
from django import forms
from django.db import connection


# Create your views here.
def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = seconds / 3600
    minutes = (seconds % 3600) / 60
    seconds = (seconds % 60)
    return days*3600*24+hours*3600+minutes*60+seconds

@login_required
def home(request):
    try:
        mymsg=request.session['toast_message']
    except:
        mymsg=""
    request.session['toast_message']=""
    list_of_elections=Election.objects.all()
    future_elections=list_of_elections.filter(vote_start_time__gt=datetime.datetime.now())

    ongoing_elections=list_of_elections.filter(vote_start_time__lt=datetime.datetime.now(), vote_end_time__gt=datetime.datetime.now())

    for x in list_of_elections:
    	print(x.vote_start_time, x.vote_end_time)
    past_elections = list_of_elections.filter(vote_end_time__lt=datetime.datetime.now()).order_by('-vote_end_time')
    return render(request,"Election_Portal/home.html",{
        'upcoming_elections':future_elections,
        'ongoing_elections':ongoing_elections,
        'past_elections':past_elections,
        'toast_message':mymsg
    })
@login_required
def nominations(request,pk):
    try:
        election=Election.objects.get(pk=pk)
    except:
        request.session['toast_message']='Nomination of this election does not exist.'
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    if election.nom_start_time<=timezone.now()<=election.nom_end_time:
        return render(request,'Election_Portal/nominations.html',{
            'election':election,
            'branches':Branch.objects.all()
        })
    else:
        request.session['toast_message']='Nominations are not yet started.' if election.nomval=="1" else "Nominations are over."
        return HttpResponseRedirect(reverse('Election_Portal:index'))
@login_required
def vote(request,pk):
    election=get_object_or_404(Election,pk=pk)
    return render(request,"Election_Portal/OnGoing.html",{
            'time_left':convert_timedelta(election.vote_end_time-timezone.now()),
            'election':election,
            'candidates':election.candidate_set.all()
        })
def nomination_filled(request,pk):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    election=get_object_or_404(Election,pk=pk)
    if election.nomval()!="2":
        request.session['toast_message']='Nominations are not yet started.' if election.nomval=="1" else "Nominations are over."
        return HttpResponseRedirect(reverse('Election_Portal:index'))
	
    elif Candidate.objects.filter(election=election,user=request.user.username).exists():
        request.session['toast_message']='You have already nominated for this election.'
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    elif Voter.objects.filter(election=election,user=request.user.username).exists():
        if request.POST:        
            candidate=Candidate(name=request.POST['name'],branch=request.POST['branch'],user=request.user.username,
                work_experience=request.POST['work'],election=election,profile_pic=request.FILES['profile_pic'])
            candidate.save()
            request.session['toast_message']='Successfully nominated.'
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    else:
        request.session['toast_message']='You are not eligible to contest this election.'
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    
@transaction.atomic
def vote_done(request,pk):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    election=get_object_or_404(Election,pk=pk)
    if Voter.objects.filter(election=election,user=request.user.username).exists():
        if request.POST:        
            voter=Voter.objects.get(election=election,user=request.user.username)
            voter.delete()
            candidate_voted=Candidate.objects.select_for_update().filter(user=request.POST['candidate'],election=election)[0]
	    candidate_voted.vote_count+=1
            candidate_voted.save()
        request.session['toast_message']='You have successfully voted.'
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    else:
        request.session['toast_message']='You are not eligible to vote.'
        return HttpResponseRedirect(reverse('Election_Portal:index'))
@login_required
def ama(request,pk):
    candidate=get_object_or_404(Candidate,pk=pk)
    if candidate.election.nomval()!="3":
        request.session['toast_message']='The AMA page is not yet live.'
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    return render(request,"Election_Portal/ama.html",{
            'candidate':candidate,
            'canEdit':candidate.election.vote_start_time>timezone.now(),
        })
@login_required
def post_comment(request,pk):
    if request.POST:    
        candidate=get_object_or_404(Candidate,pk=pk)
        comment=Comment(candidate=candidate,user=request.user.username,comment_content=request.POST['comment'],comment_time=timezone.now())
        comment.save()
        return HttpResponseRedirect(reverse('Election_Portal:ama',kwargs={'pk':pk}))
    else:
        request.session['toast_message']='Invalid form.'
        return HttpResponseRedirect(reverse('Election_Portal:index'))
@login_required
def faq(request):
    return render(request,"Election_Portal/faq.html")
@login_required
def contact(request):
    return render(request,"Election_Portal/contact.html")
@login_required
def msgsent(request):

    if request.POST:
        # email=EmailMessage('Contact Us - '+request.POST['subject'],request.POST['message']+'\n-Sent by user:'+str(request.user.username),to=['abhishek.mittal.cse17@gmail.com'])
        # email.send()
        send_mail(
            request.POST['subject'],
            request.POST['message'],
            'request.user.emailid',
            ['abhishek.mittal.cse17@itbhu.ac.in'],
            fail_silently=False,
        )
        request.session['toast_message']='Your message has been successfully sent to admin.'
    else:
        request.session['toast_message']='Invalid form.'
    return HttpResponseRedirect(reverse('Election_Portal:index'))

@login_required
def add_election(request):
    form = ElectionForm(request.POST or None)
    if form.is_valid():
        election = form.save(commit=False)
        election.save()
        userlist=User.objects.all()
        for i in userlist:
            temp=Voter()
            temp.election=election
            temp.user=i.username
            temp.save()
        return HttpResponseRedirect(reverse('Election_Portal:index'))
    context = {
        "form": form,
    }
    return render(request, 'Election_Portal/add_election.html', context)

@login_required
def show_profile(request):
    user = request.user
    try:
        profile_det = Profile.objects.get(userid=user)
    except:
        profile_det = Profile()
        profile_det.userid = request.user 
    context = {
    "profile": profile_det,
    }
    return render(request,'Election_Portal/show_profile.html',context)

@login_required
def edit_profile(request):
    uid = request.user
    fl=False
    try:
        fl=True
        profile = Profile.objects.get(userid=uid)
        data={
        'first_name':profile.first_name,
        'last_name':profile.last_name,
        'branch':profile.branch,
        'section':profile.section,
        'year':profile.year,
        'birthdate':profile.birthdate,
        'hostel':profile.hostel,
        'room':profile.room,
        'emailid':profile.emailid,
        'gender':profile.gender,
        }
        profile.delete()
    except:
        data={
        'first_name':'',
        'last_name':'',
        'year':0,
        'room':0,
        }
    form = EditProfileForm(request.POST or None,initial=data)
    if form.is_valid():
        p = form.save(commit=False)
        p.userid = request.user
        p.save()
        return HttpResponseRedirect(reverse('Election_Portal:show_profile'))
    context = {
        "form": form,
    }
    return render(request, 'Election_Portal/edit_profile.html', context)
