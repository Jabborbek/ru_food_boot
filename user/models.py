import os

# from clickuz.models import Transaction
from django.template.defaultfilters import slugify
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(verbose_name='Название категории', max_length=255)
    create_date = models.DateTimeField(auto_now_add=timezone.now)
    update_date = models.DateTimeField(auto_now=timezone.now)

    class Meta:
        verbose_name = " Категория "
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Guruh(models.Model):
    group_id = models.CharField(verbose_name='Группа ИД', max_length=255)
    create_date = models.DateTimeField(auto_now_add=timezone.now)
    update_date = models.DateTimeField(auto_now=timezone.now)

    class Meta:
        verbose_name = " Группа "
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.group_id


class Admin(models.Model):
    class Meta:
        verbose_name = " Админ "
        verbose_name_plural = " Админы "

    name = models.CharField(verbose_name='Админ ФИО', max_length=250)
    telegram = models.BigIntegerField(verbose_name='ИД телеграммы', unique=True)
    create_date = models.DateTimeField(auto_now_add=timezone.now)
    update_date = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return self.name


class User(models.Model):
    class Meta:
        verbose_name = " Пользователь "
        verbose_name_plural = " Пользователи "

    fullname = models.CharField(max_length=255, verbose_name='Пользовательский (ФИО)', null=True,
                                blank=True)
    phone = models.BigIntegerField(verbose_name='Номер пользователя', null=True, blank=True,
                                   unique=True)
    telegram = models.BigIntegerField(verbose_name='ИД телеграммы', null=True,
                                      blank=True,
                                      unique=True)
    lang = models.CharField(max_length=2, verbose_name='Язык', null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=timezone.now, verbose_name='Время создания')

    def __str__(self):
        return str(self.telegram)


class Address(models.Model):
    class Meta:
        verbose_name = " Адрес "
        verbose_name_plural = " Адреса "

    address = models.CharField(max_length=250, verbose_name='Адрес пользователя', null=True,
                               blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользовательский ФИО')

    def __str__(self):
        return self.address


class Measure(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название единицы измерения")
    create_date = models.DateTimeField(auto_now_add=timezone.now)
    update_date = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Единицы измерения продукта"
        verbose_name_plural = "Единицы измерения продукта"


class ProductQuantity(models.Model):
    measure = models.ForeignKey(Measure, on_delete=models.CASCADE,
                                verbose_name="Единица измерения")
    quantity = models.FloatField(verbose_name='Ценности', default=0.0)

    create_date = models.DateTimeField(auto_now_add=timezone.now)
    update_date = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return self.measure.name

    class Meta:
        verbose_name = "Размеры продукта"
        verbose_name_plural = "Размеры продукта"


class Product(models.Model):
    class Meta:
        verbose_name = " Продукт "
        verbose_name_plural = " Продукты "

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(max_length=250, verbose_name='Наименование товара')
    description = models.TextField(verbose_name='Информация о продукте')
    amount = models.DecimalField(verbose_name='Цена продукта', max_digits=10, decimal_places=2)
    quantity = models.FloatField(verbose_name='Oбъем продукта', default=0)
    measure = models.ManyToManyField(Measure, verbose_name="Единица измерения")
    status = models.BooleanField(verbose_name='Статус продукта', default=True)
    image = models.ImageField(verbose_name='Изображение', upload_to="products/")
    time = models.IntegerField(verbose_name="Время готовности продукта", default=0)
    create_date = models.DateTimeField(auto_now_add=timezone.now)
    update_date = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Идентификатор продукта')
    _type = models.CharField(max_length=200)
    quantity = models.CharField(max_length=200)
    amount = models.DecimalField(verbose_name='Цена', max_digits=15, decimal_places=2)
    status = models.BooleanField(default=True)
    create_date = models.DateTimeField(verbose_name='Время создания', auto_now_add=timezone.now())

    def __str__(self):
        return str(self.amount)


class SMS(models.Model):
    class Meta:
        verbose_name = " SMS "
        verbose_name_plural = " SMS "

    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    phone = models.BigIntegerField(verbose_name='Телефон номер', unique=True)
    code = models.CharField(verbose_name='СМС-код', max_length=6)
    status = models.BooleanField(verbose_name='Статус', default=False)


class Order(models.Model):
    choice = (
        ("0", "🟠 Ожидается подтверждение"),
        ("1", "🟢 Подтверждено"),
        ("2", "🔴 Отменено"),
    )
    payments_status = (
        ("0", "🟠 Ожидается платеж"),
        ("1", "🟢 Оплачено"),
        ("2", "🔴 Отменено"),
    )
    amount = models.DecimalField(verbose_name='Cтоимость', max_digits=15, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    address = models.ForeignKey(Address, on_delete=models.PROTECT, verbose_name='Адрес пользователя', null=True,
                                blank=True)
    payment_type = models.CharField(verbose_name='Адрес пользователя', choices=payments_status,
                                    max_length=55)
    pay_type = models.CharField(max_length=18, null=True, blank=True)
    admin_status = models.CharField(verbose_name='СТАТУС АДМИНИСТРАТОРА', choices=choice, max_length=30)
    status = models.BooleanField(default=True)
    distance = models.FloatField(null=True, blank=True)
    a_status = models.CharField(max_length=50, null=True, blank=True)
    create_date = models.DateField(verbose_name='Время создания')

    class Meta:
        verbose_name = " Заказ "
        verbose_name_plural = " Заказы "

    def __str__(self):
        return str(self.id)


class OrderSale(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name="Номер заказа")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Продукта')
    quantity = models.IntegerField(verbose_name='Количество', default=0)
    _type = models.CharField(max_length=200)
    amount = models.DecimalField(verbose_name='Цена', max_digits=15, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    create_date = models.DateField(verbose_name='Время создания')

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return self.product.name


class Dastavka_Price(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=1)
    _from = models.FloatField()
    _to = models.FloatField()
    create_date = models.DateTimeField(auto_now_add=timezone.now)
    update_date = models.DateTimeField(auto_now=timezone.now)

    def __str__(self):
        return 'Succesfully'

    class Meta:
        verbose_name = "Цены на доставки"
        verbose_name_plural = "Цены на доставку"
