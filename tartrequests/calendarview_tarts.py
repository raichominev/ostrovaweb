import json

from django import forms
from django.http import HttpResponse
from datetime import datetime, timedelta, time

from django.shortcuts import render_to_response
from django.template import RequestContext

from nomenclature.models import Club
from tartrequests.models import TortaRequest


def calendar_tart_data(request):

    start_parameter = request.GET['start']
    end_parameter = request.GET['end']

    start_date = datetime.strptime(start_parameter,'%Y-%m-%d')
    end_date = datetime.strptime(end_parameter,'%Y-%m-%d')
    club_id = request.GET.get('club_id', None)

    if club_id:
        tortarequests=TortaRequest.objects.filter(dostavka_date__gte=start_date,dostavka_date__lte=end_date,club_fk=club_id)
    else:
        tortarequests=TortaRequest.objects.filter(dostavka_date__gte=start_date,dostavka_date__lte=end_date)

    json_ins = []
    for tortarequest in tortarequests:
        inp = {}

        inp['title'] = str(tortarequest) + ' ,' + str(tortarequest.club_fk)
        inp['start'] = datetime.strftime(tortarequest.dostavka_date,'%Y-%m-%dT') + time.strftime(tortarequest.dostavka_time ,'%H:%M')
        inp['end'] = datetime.strftime(tortarequest.dostavka_date,'%Y-%m-%dT') + time.strftime((datetime.combine(datetime.today(), tortarequest.dostavka_time) + timedelta(hours=1)).time(),'%H:%M')
        inp['id'] = tortarequest.id
        inp['url'] = '/admin/tartrequests/tortarequest/'+str(tortarequest.id)+'/change/'
        inp['textColor'] = 'black'

        if tortarequest.status == 'NEW':
            inp['color'] = '#33ccff'
        elif tortarequest.status == 'OPEN':
            inp['color'] = '#ff4d4d'
        elif tortarequest.status == 'DELIVERED':
            inp['color'] = '#ffff80'
        elif tortarequest.status == 'PAYED':
            inp['color'] = '#85e085'
        else:
            inp['color'] = '#33ccff'


        json_ins.append(inp)

    json_txt = json.dumps(json_ins)
    return HttpResponse (json_txt)

def tortarequest_move(request):
    pass

class Form_Club(forms.Form):
    club_field = forms.ModelChoiceField(label='Клуб',queryset=Club.objects.all())

def calendar_view(request):
    context = RequestContext(request)
    form_club = Form_Club()
    if request.user.employee.club_m2m.exists():
        if request.user.employee.club_m2m.all().count() == 1:
            form_club.fields['club_field'].initial = request.user.employee.club_m2m.all()[0]
            form_club.fields['club_field'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css
        else:
            form_club.fields['club_field'].queryset = request.user.employee.club_m2m

    calendar_data={}
    calendar_data['form'] = form_club
    return render_to_response("calendar_tarts.html", calendar_data,context)
# 'form':form