import uuid

from django.db.models import Model
from django.db import models


class BaseModel(Model):
    """
     - This is a class that allows the model to inherit from any model without rewriting the id, created_at and updated_at fields.

     - This class is not created in the model because abstract=True.

     - So, the model was developed to avoid writing the above files again and again

     """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    telegram = models.CharField(max_length=25, verbose_name='ИД телеграм', unique=True)
    lang = models.CharField(max_length=2, verbose_name='Til / Язык', null=True, blank=True)

    def __str__(self):
        return 'Success'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Название категории')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категория'


class Product(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Название категории')
    name = models.CharField(max_length=250, verbose_name='Наименование товара')
    description = models.TextField(verbose_name='Информация о продукте')
    price = models.DecimalField(verbose_name='Цена продукта', max_digits=10, decimal_places=2)
    status = models.BooleanField(verbose_name='Статус продукта', default=True)
    image = models.ImageField(verbose_name='Изображение', upload_to="products/")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
