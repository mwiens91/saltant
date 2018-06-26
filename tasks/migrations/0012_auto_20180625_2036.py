# Generated by Django 2.0.6 on 2018-06-25 20:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_taskinstance_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasktype',
            name='name',
            field=models.CharField(help_text='The name of the task', max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message=('Must start with an alphabetic character [a-zA-Z] followed by word characters [a-zA-Z0-9_]',), regex='^[a-zA-Z]\\w*$')]),
        ),
    ]