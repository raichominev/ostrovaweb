from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from ostrovaweb import settings


class BaseModel(models.Model):
    class Meta:
        abstract=True
        app_label = 'Поръчка за торта'


class TortaRequest(BaseModel):
    id = models.AutoField(db_column='ID', primary_key = True, verbose_name="Ном.")

    code = models.CharField(db_column='CODE', max_length=50, blank=False, verbose_name="Кат.Номер")
    tart_type = models.CharField(db_column='TART_TYPE', max_length=50, blank=False, verbose_name="Вид")
    tart_size = models.CharField(db_column='TART_SIZE', max_length=50,blank=False, null=True, verbose_name="Големина")
    torta_cnt = models.IntegerField(db_column='TORTA_CNT', blank=False, null=True, verbose_name="Брой парчета")
    palnej = models.CharField(db_column='PALNEJ', max_length=100, blank=True, verbose_name="Пълнеж", default='-----')
    nadpis = models.CharField(db_column='NADPIS', max_length=150, blank=True, verbose_name="Надпис")

    tart_name = models.CharField(db_column='TART_NAME', max_length=100, blank=True, verbose_name="Вкус")
    price = models.FloatField(db_column='PRICE', blank=False, null=True, verbose_name="Ед.Цена")

    notes = models.TextField(db_column='NOTES', max_length=3000, blank=True, verbose_name="Забележка")

    dostavka_date = models.DateTimeField(db_column='DOSTAVKA_DATE', blank=False, null=True, verbose_name="Дата доставка")
    delivery_address  = models.TextField(db_column='DELIVERY_ADDRESS', max_length=1000, blank=True, verbose_name="Адрес на доставка")
    client_phone = models.CharField(db_column='CLIENT_PHONE', max_length=50, blank=True, verbose_name="Телефон")

    changes = models.TextField(db_column='CHANGES', max_length=3000, blank=True, verbose_name="История на промените")
    reg_date = models.DateTimeField(db_column='REG_DATE', blank=False, null=False, verbose_name="Дата заявка", default=timezone.now)
    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна")
    user_fk = models.ForeignKey(User, to_field='id',db_column='USER_ID', verbose_name="Заявител")
    club_fk = models.ForeignKey('nomenclature.Club', to_field='club_id',db_column='CLUB_ID', verbose_name="Клуб", default=1)

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

    class Meta:
        managed = True
        db_table = 'tart_req'
        verbose_name = u"Заявка за торта"
        verbose_name_plural = u"Заявки за торта"

    def __str__(self):
        return str(self.tart_type) + ':' + str(self.code) + ":" + str(self.tart_name)


class TortaTasteRegister(BaseModel):

    palnej = models.CharField(max_length=50, blank=True, verbose_name="Пълнеж")
    level = models.IntegerField(blank=False, null=False, verbose_name="Макс. Етаж")
    price = models.FloatField(blank=False, null=True, verbose_name="Ед.Цена")

    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна", default=timezone.now)

    class Meta:
        managed = True
        db_table = 'tart_taste_register'
        verbose_name = u"Вкус за торта"
        verbose_name_plural = u"Вкусове за торта"

    def __str__(self):
        return self.palnej + ':' + str(self.level)


class TortaRequestPicture(BaseModel):

    torta_rq_fk = models.ForeignKey( to=TortaRequest, db_column='tart_id', to_field='id')
    filename = models.FileField(upload_to=settings.TARTIMAGES_STORAGE + "/" + settings.TART_CUSTOM_REQESTS_FOLDER, max_length=100,  blank = True, null= True, verbose_name="Изображение")
    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна",default=timezone.now)

    class Meta:
        managed = False
        db_table = 'tart_req_pictures'
        verbose_name = u"Собствено изображение за торта"
        verbose_name_plural = u"Собствени изображения за торта"

    def __str__(self):
        return str(self.filename)


# class TortaRequestTaste(BaseModel):
#
#     rec_no = models.IntegerField(blank=False, null=True, verbose_name="Етаж")
#     torta_rq_fk = models.ForeignKey( to=TortaRequest, db_column='tart_id', to_field='id')
#     torta_taste_fk = models.ForeignKey( to=TortaTasteRegister, to_field='id')
#     price = models.FloatField(db_column='PRICE', blank=False, null=True, verbose_name="Ед.Цена")
#
#     class Meta:
#         managed = True
#         db_table = 'tart_req_taste'
#         verbose_name = u"Вкус за торта (заявка)"
#         verbose_name_plural = u"Вкусове за торта (заявка)"
#
#     def __str__(self):
#         return str(self.torta_taste_fk)


class TortaPictureRegister(BaseModel):

    def upload_storage(self,name):
        return settings.TARTIMAGES_STORAGE + "/" + self.category + "/" + name

    filename = models.FileField(upload_to=upload_storage, max_length=200,  blank = True, null= True, verbose_name="Изображение")
    code = models.CharField(max_length=50, blank=True, verbose_name="Код")
    tart_type = models.CharField(max_length=50, blank=True, verbose_name="Тип", choices=(
        ('3D','3D'),
        ('Захарна плака','Захарна плака'),
        ('Стандартна','Стандартна'),)
                                 )

    category = models.CharField(max_length=150, blank=True, verbose_name="Категория")
    description = models.TextField(max_length=400, blank=True, verbose_name="Описание")
    last_update_date = models.DateTimeField(db_column='LAST_UPDATE_DATE', blank=True, null=True, verbose_name="Дата промяна",default=timezone.now)

    torta_tase_fk = models.ManyToManyField('TortaTasteRegister', verbose_name="Вкусове")

    class Meta:
        managed = True
        db_table = 'tart_picture_register'
        verbose_name = u"Регистър на торти"
        verbose_name_plural = u"Регистър на торти"

    def __str__(self):
        return str(self.filename)


class TortaPieceCoding(BaseModel):

    tart_type = models.CharField(max_length=50, verbose_name="Тип", choices=(
        ('3D','3D'),
        ('Захарна плака','Захарна плака'),
        ('Стандартна','Стандартна'),)
                                 )
    torta_cnt = models.IntegerField(db_column='TORTA_CNT',  verbose_name="Брой парчета")
    levels = models.IntegerField(db_column='LEVLES',  verbose_name="Етажи")

    tart_size = models.CharField(db_column='TART_SIZE', max_length=50, verbose_name="Описание")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.tart_size = str(self.levels) + " ет. " + str(self.torta_cnt) + ' парчета'
        super(TortaPieceCoding, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        managed = True
        db_table = 'tart_piece_coding'
        verbose_name = u"Брой Парчета"
        verbose_name_plural = u"Брой Парчета"

    def __str__(self):
        return str(self.tart_size)
