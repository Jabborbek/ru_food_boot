# Generated by Django 4.2.3 on 2023-07-18 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_category_name_af_remove_category_name_ar_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Категория', 'verbose_name_plural': 'Категории'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Продукт', 'verbose_name_plural': 'Продукты'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name': 'Подкатегория', 'verbose_name_plural': 'Подкатегории'},
        ),
    ]
