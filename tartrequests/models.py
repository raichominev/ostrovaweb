from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import timezone

from ostrovaweb import settings


TART_TYPES = (
    ('3D','3D'),
    ('Захарна плака','Захарна плака'),
    ('Стандартна','Стандартна'),)

class TortaDeliveryAddress(models.Model):
    delivery_address  = models.CharField(db_column='DELIVERY_ADDRESS', max_length=1000, verbose_name="Адрес на доставка")
    group = models.ForeignKey(Group, verbose_name="Група")

    class Meta:
        managed = True
        verbose_name = u"Адрес за доставка"
        verbose_name_plural = u"Адреси за доставка"

    def __str__(self):
        return str(self.group) + ':' + str(self.delivery_address)


class TortaRequest(models.Model):
    id = models.AutoField(db_column='ID', primary_key = True, verbose_name="Рег. Номер  ")

    code = models.ForeignKey('TortaPictureRegister', verbose_name="Кат.No.")
    tart_size = models.ForeignKey('TortaPieceCoding', db_column='TART_SIZE', blank=False, null=True, verbose_name="Големина")
    palnej = models.ForeignKey('TortaTasteRegister',db_column="PALNEJ",  verbose_name="Пълнеж")
    nadpis = models.CharField(db_column='NADPIS', max_length=150, blank=True, verbose_name="Надпис", default='Честит рожден ден')

    notes = models.TextField(db_column='NOTES', max_length=3000, null=True, blank=True, verbose_name="Забележка")

    dostavka_date = models.DateField(blank=False, null=True, verbose_name="Дата доставка")
    dostavka_time = models.TimeField(blank=False, null=True, verbose_name="Час")
    delivery_address  = models.TextField(db_column='DELIVERY_ADDRESS', max_length=1000, blank=True, null=True, verbose_name="Адрес на доставка")
    client_phone = models.CharField(db_column='CLIENT_PHONE', max_length=50, blank=True, verbose_name="Телефон")

    reg_date = models.DateTimeField(db_column='REG_DATE', blank=False, null=False, verbose_name="Дата заявка", default=timezone.now)
    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна")
    user_fk = models.ForeignKey(User, to_field='id',db_column='USER_ID', verbose_name="Заявител")
    club_fk = models.ForeignKey('nomenclature.Club', verbose_name="Клуб")

    status = models.CharField(db_column='STATUS', max_length=50, blank=False, verbose_name="Статус", choices=(
        ('NEW','Нова'),
        ('OPEN','Заявена'),
        ('DELIVERED','Доставена'),
        ('PAYED','Платена'),
    ), default='NEW')

    #payment_date = models.DateTimeField(db_column='PAYMENT_DATE', blank=True, null=True, verbose_name="Дата валидност")
    #payment_doc = models.CharField(db_column='PAYMENT_DOC', max_length=50, blank=True, verbose_name="Документ Плащане")
    #partiden_no = models.CharField(db_column='PARTIDEN_NO', max_length=50, blank=True, verbose_name="Партиден номер")
    #validity_date = models.DateTimeField(db_column='VALIDITY_DATE', blank=True, null=True, verbose_name="Дата валидност")
    #faktura_no = models.CharField(db_column='FAKTURA_NO', max_length=100, blank=True)
    #faktura_date = models.DateTimeField(db_column='FAKTURA_DATE', blank=True, null=True, verbose_name="Дата фактура")

    def actual_picture(self):
        if self.tortarequestpicture_set.all().exists():
            return self.tortarequestpicture_set.first().filename
        else:
            return self.code.filename

    class Meta:
        managed = True
        db_table = 'tart_req'
        verbose_name = u"Заявка за торта"
        verbose_name_plural = u"Заявки за торта"

        default_permissions = ()
        permissions = (
            ('change_tortarequest','Променя Заявка за торта'),
            ('add_tortarequest','Добавя Заявка за торта'),
            ('delete_tortarequest','Изтрива Заявка за торта'),
            ('view_tortarequest_calendar', 'Календар за Заявка за торта')
        )

    def __str__(self):
        return str(self.code) + ":" + str(self.tart_size) + ':' + str(self.palnej)


class TortaPricePerClub(models.Model):
    club_fk = models.ForeignKey('nomenclature.Club', verbose_name="Клуб")
    tart_type = models.CharField(max_length=50, blank=True, verbose_name="Тип", choices=TART_TYPES)

    price = models.DecimalField(max_digits = 8, decimal_places=2, verbose_name="Ед.Цена")

    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна", default=timezone.now)

    class Meta:
        managed = True
        db_table = 'tart_prices'
        verbose_name = u"Цена за торта"
        verbose_name_plural = u"Цени за торти"

    def __str__(self):
        return str(self.club_fk) + ':' + str(self.tart_type) + '=' + str(self.price)

class TortaTasteRegister(models.Model):

    palnej = models.CharField(max_length=50, blank=True, verbose_name="Пълнеж")
    level = models.IntegerField(blank=False, null=False, verbose_name="Макс. Етаж")

    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна", default=timezone.now)

    class Meta:
        managed = True
        db_table = 'tart_taste_register'
        verbose_name = u"Вкус за торта"
        verbose_name_plural = u"Вкусове за торта"

    def __str__(self):
        return self.palnej


class TortaRequestPicture(models.Model):

    torta_rq_fk = models.ForeignKey( to=TortaRequest, db_column='tart_id', to_field='id')
    filename = models.FileField(upload_to=str(settings.TARTIMAGES_STORAGE + "/" + settings.TART_CUSTOM_REQESTS_FOLDER), max_length=100,  blank = True, null= True, verbose_name="Изображение")
    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна",default=timezone.now)

    class Meta:
        managed = True
        db_table = 'tart_req_pictures'
        verbose_name = u"Собствено изображение за торта"
        verbose_name_plural = u"Собствени изображения за торта"

    def __str__(self):
        return str(self.filename)


class TortaPictureRegister(models.Model):

    def short_tart_type(self, type):
        return {
            '3D':'3D',
            'Захарна плака':'З.Плака',
            'Стандартна':'Стд.'
        }.get(type,type)

    def upload_storage(self,name):
        return settings.TARTIMAGES_STORAGE + "/" + self.category.category + "/" + name

    filename = models.FileField(upload_to=upload_storage, max_length=200,  blank = True, null= True, verbose_name="Изображение")
    code = models.CharField(unique=True,max_length=50, verbose_name="Код")
    tart_type = models.CharField(max_length=50, blank=True, verbose_name="Тип", choices=TART_TYPES)

    category = models.ForeignKey( to='TortaPictureCategory', verbose_name="Категория")
    description = models.TextField(max_length=400, blank=True, verbose_name="Описание")
    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна",default=timezone.now)

    class Meta:
        managed = True
        db_table = 'tart_picture_register'
        verbose_name = u"Вид на торта"
        verbose_name_plural = u"Видове торти"

    def __str__(self):
        return str(self.code) # + ':' + str(self.short_tart_type(self.tart_type)) + ':' + str(self.category)


class TortaPieceCoding(models.Model):

    tart_type = models.CharField(max_length=50, verbose_name="Тип", choices=TART_TYPES)
    torta_cnt = models.IntegerField(db_column='TORTA_CNT',  verbose_name="Брой парчета")
    levels = models.IntegerField(db_column='LEVLES',  verbose_name="Етажи")

    tart_size = models.CharField(db_column='TART_SIZE', max_length=50, verbose_name="Описание")

    club_m2m = models.ManyToManyField('nomenclature.Club', verbose_name="За клуб")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.tart_size = str(self.levels) + " ет. " + "%02d" % self.torta_cnt + ' парчета'
        super(TortaPieceCoding, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        managed = True
        db_table = 'tart_piece_coding'
        verbose_name = u"Брой Парчета"
        verbose_name_plural = u"Брой Парчета"

    def __str__(self):
        return str(self.tart_size)


class TortaPictureCategory(models.Model):
    category = models.CharField(max_length=150, blank=True, verbose_name="Категория")

    class Meta:
        managed = True
        db_table = 'tart_category'
        verbose_name = u"Категория"
        verbose_name_plural = u"Категории"

    def __str__(self):
        return str(self.category)
