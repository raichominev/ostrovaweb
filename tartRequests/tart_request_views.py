# coding=utf-8
import json
import logging

from django.contrib import messages

from ostrovaApp.clever_select_enhanced.views import ChainedSelectChoicesView
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers
from django.views.generic.detail import BaseDetailView

from ostrovaApp.models import TortaPictureRegister, TortaPieceCoding, TortaRequest, TortaTasteRegister

symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
           u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
tr = dict([(ord(a), ord(b)) for (a, b) in zip(*symbols)])

symbols_reverse = (u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA",
            u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
tr_reverse = dict([(ord(a), ord(b)) for (a, b) in zip(*symbols_reverse)])


def fix_code(code):
    return code.translate(tr).upper()

def fix_code_reverse(code):
    return code.translate(tr_reverse).upper()

def get_tart_model(code):
    try:
        return TortaPictureRegister.objects.get(code=fix_code(code))
    except TortaPictureRegister.DoesNotExist:
        return TortaPictureRegister.objects.get(code=fix_code_reverse(code))


class TartRequestAjaxChainedView(ChainedSelectChoicesView):
    """
    View to handle the ajax request for the field options.
    """

    def get_choices(self,request):
        vals_list = []

        logging.info("field:" + self.field)
        logging.info(u"parent_value:" + unicode(self.parent_value))

        if self.field == 'tart_type':
            tortaDescr = get_tart_model(self.parent_value)

            vals_list.append(tortaDescr.tart_type)

        if self.field == 'tart_name':
            tortaDescr = get_tart_model(self.parent_value)

            vals_list.append(tortaDescr.category)

        if self.field == 'tart_size':
            vals_list = [x.id for x in TortaPieceCoding.objects.filter(tart_type = self.parent_value).order_by('tart_size')]
            descr_list = [x.tart_size for x in TortaPieceCoding.objects.filter(tart_type = self.parent_value).order_by('tart_size')]

            return tuple(zip(vals_list, descr_list))

        if self.field == 'torta_cnt':
            vals_list.append(TortaPieceCoding.objects.get(id = self.parent_value).torta_cnt)

        if self.field.endswith('torta_taste_fk'):
            #logging.info("parent_value:" + str(self.parent_value))
            #tortaReq = TortaRequest.objects.get(id=self.parent_value)
            #logging.info(u"parent_value:" + unicode(tortaReq))
            tortaDescr = get_tart_model(self.parent_value)

            # messages.info(request, u"parent_value:" + unicode(tortaDescr))
            descr_list=[]
            for x in tortaDescr.torta_tase_fk.all():
                vals_list.append(x.id)
                descr_list.append(x.palnej)
            return tuple(zip(vals_list, descr_list))

        if self.field.endswith('price'):
            vals_list.append(TortaTasteRegister.objects.get(id = self.parent_value).price)

        if self.field == 'tart_price':
            vals_list = ['0','0']

        return tuple(zip(vals_list, vals_list))

