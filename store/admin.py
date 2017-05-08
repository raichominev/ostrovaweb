from django.contrib import admin
from reversion_compare.admin import CompareVersionAdmin


class ArticleStoreAdmin(CompareVersionAdmin):
    readonly_fields = ('id',)
    list_display = ('id','club_fk','article_fk', 'cnt', 'cnt_min', 'cnt_bl','note')
    search_fields = ('article_fk__name',)
    raw_id_fields = ('article_fk',)

admin.site.register(ArticleStore, ArticleStoreAdmin)

class stock_delivery_detail_inline(admin.TabularInline):
    model = stock_delivery_detail
    fields = ('article_store_fk', 'cnt')
    readonly_fields = ()
    extra = 5

    raw_id_fields = ("article_store_fk",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.closed:
            return self.fields
        return self.readonly_fields

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.closed:
            return 0
        return self.extra

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and obj.closed:
            return 0
        return self.max_num

    def has_delete_permission(self, request, obj=None):
        if obj and obj.closed:
            return False
        return True


class stock_acceptance_detail_inline(admin.TabularInline):
    model = stock_acceptance_detail
    fields = ('article_store_fk', 'cnt')
    readonly_fields = ()
    extra = 5

    raw_id_fields = ("article_store_fk",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.closed:
            return self.fields
        return self.readonly_fields

    def get_extra(self, request, obj=None, **kwargs):
        if obj and obj.closed:
            return 0
        return self.extra

    def get_max_num(self, request, obj=None, **kwargs):
        if obj and obj.closed:
            return 0
        return self.max_num

    def has_delete_permission(self, request, obj=None):
        if obj and obj.closed:
            return False
        return True


class stock_receipt_protocolForm(ModelForm):
    def clean_transfer_club_fk(self):
        form_data = self.cleaned_data
        if 'transfer_club_fk' in form_data and form_data['club_fk'] == form_data['transfer_club_fk']:
            raise ValidationError("Моля изберете различен обект, към който да се извърши трансфера")
        return form_data['transfer_club_fk']


class stock_receipt_protocolAdmin(DjangoObjectActions, CompareVersionAdmin):

    list_display =('type','id','receipt_date', 'club_fk','transfer_club_fk' )
    readonly_fields = ('id','order_fk' ,'delivery_fk','transfer_fk','receipt_date', 'closed')
    form = stock_receipt_protocolForm

    def get_fields(self, request, obj=None):
        if obj and obj.type == 'ORDER':
            return 'id', 'type', 'club_fk', 'receipt_date', 'order_fk', 'closed', 'note',
        if obj and obj.type == 'DELIVERY':
            return 'id', 'type', 'club_fk', 'receipt_date', 'delivery_fk','closed', 'note',
        if obj and obj.type in  ('EXPDELIVERY','EXPEDITION'):
            return 'id', 'type', 'club_fk', 'receipt_date', 'transfer_fk','transfer_club_fk','closed', 'note',

        return 'id', 'type', 'club_fk', 'receipt_date','closed','note',

    def get_form(self, request, obj=None, **kwargs):

        form = super(stock_receipt_protocolAdmin, self).get_form(request, obj,**kwargs)

        if not obj:
            # remove ORDER and DELIVERY, since they are only added automatically
            form.base_fields['type'].choices = stock_receipt_protocol.MANUAL_TYPES

        # if editing (obj will be filled in with the existing model)
        if obj and not obj.closed:
            form.base_fields['type'].disabled = True
            form.base_fields['club_fk'].disabled = True

            if obj.transfer_club_fk:
                form.base_fields['transfer_club_fk'].disabled = True

        # if club is specified for the current user (in the user model), do not allow choosing another club
        if request.user.employee.club_fk and not obj.closed:
            form.base_fields['club_fk'].initial = request.user.employee.club_fk
            form.base_fields['club_fk'].widget.attrs.update({'readonly':'True','style':'pointer-events:none'})  # simulates readonly on the browser with the help of css

        return form

    inlines = [
        stock_delivery_detail_inline,
        stock_acceptance_detail_inline,
    ]

    def get_inline_instances(self, request, obj=None):
        inline_instances = super(stock_receipt_protocolAdmin, self).get_inline_instances(request,obj)

        # for new instances do not allow inlines - this way the protocol type will be initially set, then after
        # save and reload the appropriate inline types will be allowed only
        if not obj:
            return []

        # remove specific inlines that are not applicable depending on protocol type

        fixed_inline_instances = []
        for inline in inline_instances:
            if obj and obj.type in ('ORDER','LATEORD','SCRAP','INTERNAL','EXPEDITION') and isinstance(inline, stock_acceptance_detail_inline):
                continue
            if obj and obj.type in ('DELIVERY','CORDELIVERY','EXPDELIVERY') and isinstance(inline, stock_delivery_detail_inline):
                continue
            fixed_inline_instances.append(inline)

        return fixed_inline_instances

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.closed:
            return self.get_fields(request, obj)
        return self.readonly_fields

    def stock_receipt_protocol_close(self, request, obj):

        # check if closed
        if obj.closed:
            messages.error(request,"Този протокол вече е приключен.")
            return

        ########################################################
        # check Article Store availability

        # if Article is missing from ArticleStore -print error and abort
        checked = True
        for stock_dev in obj.stock_delivery_detail_set.all():
            if stock_dev.article_store_fk.cnt - nvl(stock_dev.article_store_fk.cnt_bl,0) < stock_dev.cnt:
                messages.info(request,"Няма достатъчна наличност в склада за %s. налични:%d, блокирани:%d, не достигат: %d" % (str(stock_dev.article_store_fk.article_fk),stock_dev.article_store_fk.cnt,stock_dev.article_store_fk.cnt_bl, stock_dev.cnt - (stock_dev.article_store_fk.cnt - stock_dev.article_store_fk.cnt_bl) ) )
                checked = False

        # if transfer create a mirror protocol in other club
        if checked:

            #########################################################
            # add/substract quantities to ArticleStore
            for stock_dev in obj.stock_delivery_detail_set.all():
                # modify Article Store entry by sustracting quantity
                stock_dev.article_store_fk.cnt = stock_dev.article_store_fk.cnt - stock_dev.cnt
                stock_dev.article_store_fk.save()


            for stock_dev in obj.stock_acceptance_detail_set.all():
                # modify Article Store entry by adding quantity
                stock_dev.article_store_fk.cnt = stock_dev.article_store_fk.cnt + stock_dev.cnt
                stock_dev.article_store_fk.save()

            if obj.type == 'EXPEDITION':

                #########################################################
                # add record to protocols

                stock_doc = stock_receipt_protocol()
                stock_doc.transfer_fk = obj
                stock_doc.club_fk = obj.transfer_club_fk
                stock_doc.transfer_club_fk = obj.club_fk
                stock_doc.receipt_date = datetime.now()
                stock_doc.type = 'EXPDELIVERY'
                stock_doc.note = 'Протокол към трансфер Номер %d' % (obj.id,)
                stock_doc.closed = True
                stock_doc.save()

                obj.transfer_fk = stock_doc

                #########################################################
                # add each order article as stock delivery detail within the newly created protocol
                for stock_dev in obj.stock_delivery_detail_set.all():

                    # lookup store from the other side
                    try:
                        artstore = ArticleStore.objects.get(club_fk = obj.transfer_club_fk, article_fk = stock_dev.article_store_fk.article_fk)
                    except ArticleStore.DoesNotExist:
                        artstore = ArticleStore()
                        artstore.club_fk = obj.transfer_club_fk
                        artstore.article_fk = stock_dev.article_store_fk.article_fk
                        artstore.cnt = 0
                        artstore.cnt_min = 0
                        artstore.cnt_bl = 0

                    artstore.cnt +=  stock_dev.cnt
                    artstore.save()

                    #########################################################
                    # create a corresponding acceptance detail
                    stock_acc = stock_acceptance_detail()
                    stock_acc.stock_protocol_fk = stock_doc
                    stock_acc.article_store_fk = artstore
                    stock_acc.cnt = stock_dev.cnt
                    stock_acc.save()

                messages.info(request,"Добавен е протокол за трансфер от склада. от номер:%d към номер:%d" % (obj.id,stock_doc.id, ) )

            obj.closed = True
            obj.save()
        else:

            messages.error(request,"Не е приключен е протокол за изписване от склада" )


            #todo: validate for negative quantities


    stock_receipt_protocol_close.label = "Приключване"  # optional
    stock_receipt_protocol_close.short_description = "Приключване на протокол"  # optional

    change_actions = ('stock_receipt_protocol_close', )


admin.site.register(stock_receipt_protocol, stock_receipt_protocolAdmin)

