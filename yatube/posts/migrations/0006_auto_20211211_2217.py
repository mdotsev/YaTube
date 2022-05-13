# Generated by Django 2.2.9 on 2021-12-11 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20211208_2217'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['pub_date']},
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
