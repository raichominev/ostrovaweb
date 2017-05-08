from django.contrib import admin
from django.forms import ModelForm
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy

from nomenclature.models import ArticleGroup
from order.models import *
from clever_select_enhanced.forms import ChainedChoicesModelForm
from clever_select_enhanced.clever_txt_field import ChainedNumberInputField

from django_object_actions import DjangoObjectActions
from reversion_compare.admin import CompareVersionAdmin

class OrderDetailForm(ChainedChoicesModelForm):

    price = ChainedNumberInputField(parent_field='article_fk', ajax_url=reverse_lazy('article_ajax_chained_order_models'),
                                    label=u'Цена', required=True)

    class Meta:
        model = OrderDetail
        fields = '__all__'

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    form = OrderDetailForm
    #    select_related = ('group', 'article')

    raw_id_fields = ( 'article_fk',)


class OrderAdmin(DjangoObjectActions, CompareVersionAdmin):

    change_list_template = "admin/order/order/change_list.html"
    search_fields = ('child','parent','phone',)
    list_filter = (
        'rec_date','club_fk',
    )

    ordering = ['-id']
    list_per_page = 50

    date_hierarchy = "rec_date"
    readonly_fields = ('store_status','locked')
    list_display = ('rec_date', 'club_fk', 'rec_time', 'parent', 'child', 'locked', 'payed_final',)
    fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ['club_fk','rec_date','rec_time','rec_time_end','rec_time_slot','locked','store_status','user']
        }),

        ('Клиент', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ['parent','phone','child','age','child_count','adult_count','saloon_fk','address','email',]
        }),

        ('Плащане1', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ['deposit','discount','price_final','payment_date',]
        }),

        ('Плащане2', {
            'classes': ('suit-tab', 'suit-tab-club',),
            'fields': ['deposit2_date','deposit2','payed_final',]
        }),

        ('Забележка', {
            'classes': ('suit-tab', 'suit-tab-notes',),
            'fields': ['order_date', 'create_date','last_update_date','changes','update_state','notes','refusal_date','refusal_reason','notes_torta','notes_kitchen',]
        }),
    ]

    suit_form_tabs = (('club', 'Поръчка за парти'),
                      # ('order', 'Поръчка за парти'),
                      # ('client', 'Client'),
                      #('paymends1', 'Paymends1'),
                      #('paymends2', 'Paymends2'),
                      ('notes', 'Забележки'))

    def locked(self, obj):
        return len(obj.locked_set.all())

    def suit_row_attributes(self, obj):
        class_locked = {
            '0': 'success',
            '1': 'warning',
        }
        css_class = class_locked.get(obj.locked)
        if css_class:
            return {'class': css_class}

    def suit_cell_attributes(self, obj, column):
        if column == 'locked':
            return {'class': 'text-center'}
        elif column == 'right_aligned':
            return {'class': 'text-right muted'}

    inlines = [
        OrderDetailInline,
    ]

    def save_model(self, request, obj, form, change):

        if 'deposit' in form.changed_data and form.cleaned_data['deposit'] > 0:
            payment_doc = Cashdesk_detail_income()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.deposit
            payment_doc.note = str(obj)
            payment_doc.cashdesk_groups_income_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = Cashdesk.objects.filter(club_fk=obj.club_fk).latest('id')

            payment_doc.save()

            messages.info(request,"Добавено плащане капаро за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        if 'deposit2' in form.changed_data and form.cleaned_data['deposit2'] > 0:
            payment_doc = Cashdesk_detail_income()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.deposit2
            payment_doc.note = str(obj)
            payment_doc.cashdesk_groups_income_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = Cashdesk.objects.filter(club_fk=obj.club_fk).latest('id')

            payment_doc.save()

            messages.info(request,"Добавено плащане капаро 2 за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        if 'payed_final' in form.changed_data and form.cleaned_data['payed_final'] > 0:
            payment_doc = Cashdesk_detail_income()

            payment_doc.order_fk = obj
            payment_doc.amount = obj.payed_final
            payment_doc.note = str(obj)
            payment_doc.cashdesk_groups_income_fk = Cashdesk_groups_income.objects.get(name='ПОРЪЧКА',sub_name='ПЛАЩАНЕ')
            payment_doc.cashdesk = Cashdesk.objects.filter(club_fk=obj.club_fk).latest('id')

            payment_doc.save()

            messages.info(request,"Добавено финално плащане за %.2f лв. Номер:%d, Каса:%s " % (payment_doc.amount,payment_doc.id, str(payment_doc.cashdesk)))

        super(OrderAdmin, self).save_model(request, obj, form, change)

    def take_out_of_store(self, request, obj):
        ########################################################
        # if Article is missing from ArticleStore -print error and abort save
        if obj.store_status:
            messages.error(request,"Поръчката вече е изписана" )

        checked = True
        for ord in obj.orderdetail_set.all():
            try:
                artstore = ArticleStore.objects.get(club_fk = obj.club_fk, article_fk = ord.article_fk)
            except ArticleStore.DoesNotExist:
                messages.info(request,"За артикул %s няма запис в склада. Моля извършете доставка или трансфер." % (str(ord.article_fk),) )
                checked = False
                continue

            if  artstore.cnt - artstore.cnt_bl < ord.cnt:
                messages.info(request,"Няма достатъчна наличност в склада за %s. налични:%d, блокирани:%d, не достигат: %d" % (str(ord.article_fk),artstore.cnt,artstore.cnt_bl, ord.cnt - (artstore.cnt - artstore.cnt_bl) ) )
                checked = False

        if checked:

            #########################################################
            # add record to protocols

            stock_doc = stock_receipt_protocol()
            stock_doc.order_fk = obj
            stock_doc.club_fk = obj.club_fk
            stock_doc.receipt_date = datetime.now()
            stock_doc.type = 'ORDER'
            stock_doc.note = 'Протокол към поръчка Номер %d Дата:%s' % (obj.id,obj.rec_date)
            stock_doc.closed = True
            stock_doc.save()

            #########################################################
            # add each order article as stock delivery detail within the newly created protocol
            for ord in obj.orderdetail_set.all():

                # modify Article Store entry by sustracting quantity
                artstore = ArticleStore.objects.get(club_fk = obj.club_fk, article_fk = ord.article_fk)

                #substract from artstore
                artstore.cnt = artstore.cnt - ord.cnt
                artstore.save()

                stock_del = stock_delivery_detail()
                stock_del.stock_protocol_fk = stock_doc
                stock_del.article_store_fk = artstore
                stock_del.orderdetail_fk = ord
                stock_del.cnt = ord.cnt
                stock_del.save()

            messages.info(request,"Добавен е протокол за изписване от склада. Номер:%d" % (stock_doc.id, ) )

            obj.store_status = True
            obj.save()
        else:
            messages.error(request,"Не е добавен е протокол за изписване от склада" )

    take_out_of_store.label = "Изписване"  # optional
    take_out_of_store.short_description = "Изписване от слкада"  # optional

    change_actions = ('take_out_of_store', )

admin.site.register(Order, OrderAdmin)


class ArticleOrderForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super(ArticleOrderForm, self).__init__(*args,**kwargs)
        self.fields['group_fk'].queryset=ArticleGroup.objects.filter(order_type = True)

class ArticleOrderAdmin(admin.ModelAdmin):
    fields = ('id','name', 'description','measure','last_update_date','group_fk','sale_price',)
    list_display =('name','group_fk','description','measure','delivery_price','sale_price',)
    readonly_fields = ('last_update_date','id',)
    form = ArticleOrderForm

    list_filter = (
        ('group_fk', admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ('name', 'description')

admin.site.register(ArticleOrder, ArticleOrderAdmin)