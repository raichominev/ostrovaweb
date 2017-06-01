"""ostrovaweb URL Configuration
"""
from django.conf.urls import url, include
from django.contrib import admin

from nomenclature.article_views import ArticleAjaxChainedView, ArticleAjaxOrderChainedView, article_name_lookup
from order import calendarview
from tartrequests import calendarview_tarts
from tartrequests.tart_request_views import TartRequestAjaxChainedView

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^fullcalendar/', calendarview.calendar_view, name='fullcalendar'),
    url(r'^calendar_orders_feed/', calendarview.calendar_order_data, name='calendar_orders_feed'),

    url(r'^fullcalendartarts/', calendarview_tarts.calendar_view, name='fullcalendar_tarts'),
    url(r'^calendar_tarts_feed/', calendarview_tarts.calendar_tart_data, name='calendar_tarts_feed'),

    url(r'^admin/ajax/article-chained/$', ArticleAjaxChainedView.as_view(), name='article_ajax_chained_models'),
    url(r'^admin/ajax/article-chained-order/$', ArticleAjaxOrderChainedView.as_view(), name='article_ajax_chained_order_models'),
    url(r'^article_name_lookup/', article_name_lookup, name='article_name_lookup'),

    url(r'^admin/ajax/torta-request-chained/$', TartRequestAjaxChainedView.as_view(), name='torta_request_ajax_chained_models'),

    url(r'^select2/', include('django_select2.urls')),
]
