# coding=utf-8
import json
import logging

from django.contrib import messages

from clever_select_enhanced.views import ChainedSelectChoicesView
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers
from django.views.generic.detail import BaseDetailView

from ostrovaweb.utils import fix_code, fix_code_reverse
from tartrequests.models import TortaPictureRegister, TortaPieceCoding, TortaRequest, TortaTasteRegister

def get_tart_model(id):
    return TortaPictureRegister.objects.get(id=id)

class TartRequestAjaxChainedView(ChainedSelectChoicesView):
    """
    View to handle the ajax request for the field options.
    """

    def get_choices(self,request):
        vals_list = []

        logging.info("field:" + self.field)
        logging.info(u"parent_value:" + str(self.parent_value))

        # if self.field == 'tart_type':
        #     tortaDescr = get_tart_model(self.parent_value)
        #
        #     vals_list.append(tortaDescr.tart_type)
        #
        # if self.field == 'tart_name':
        #     tortaDescr = get_tart_model(self.parent_value)
        #
        #     vals_list.append(tortaDescr.category.category)

        if self.field == 'tart_size':
            tortaType = TortaPictureRegister.objects.get(id=self.parent_value)
            pieceCodings =  TortaPieceCoding.objects.filter(tart_type = tortaType.tart_type).order_by('tart_size')

            vals_list = [x.id for x in pieceCodings]
            descr_list = [x.tart_size for x in pieceCodings]

            return tuple(zip(vals_list, descr_list))

        if self.field == 'zz_tart_type':
            tortaType = TortaPictureRegister.objects.get(id=self.parent_value)
            return tuple(zip(tortaType.tart_type, tortaType.tart_type))

        if self.field == 'zz_tart_category':
            tortaType = TortaPictureRegister.objects.get(id=self.parent_value)
            return tuple(zip(str(tortaType.category), str(tortaType.category)))

        if self.field == 'palnej':
            pieceCoding = TortaPieceCoding.objects.get(id=self.parent_value)
            tastes =  TortaTasteRegister.objects.filter(level__gte = pieceCoding.levels).order_by('id')

            vals_list = [x.id for x in tastes]
            descr_list = [x.palnej for x in tastes]

            return tuple(zip(vals_list, descr_list))


        # if self.field.endswith('torta_taste_fk'):
        #     #logging.info("parent_value:" + str(self.parent_value))
        #     #tortaReq = TortaRequest.objects.get(id=self.parent_value)
        #     #logging.info(u"parent_value:" + unicode(tortaReq))
        #     tortaDescr = get_tart_model(self.parent_value)
        #
        #     # messages.info(request, u"parent_value:" + unicode(tortaDescr))
        #     descr_list=[]
        #     for x in tortaDescr.torta_tase_fk.all():
        #         vals_list.append(x.id)
        #         descr_list.append(x.palnej)
        #     return tuple(zip(vals_list, descr_list))
        #
        # if self.field.endswith('price'):
        #     vals_list.append(TortaTasteRegister.objects.get(id = self.parent_value).price)
        #
        # if self.field == 'tart_price':
        #     vals_list = ['0','0']

        return tuple(zip(vals_list, vals_list))

