# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=255)),
                ('key', models.CharField(unique=True, max_length=40)),
                ('set_at', models.DateTimeField(default=django.utils.timezone.now, help_text='When the confirmation key expiration was set')),
                ('confirmed_at', models.DateTimeField(help_text='First time this email was confirmed', null=True, blank=True)),
                ('user', models.ForeignKey(related_name='email_address_set', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'email addresses',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='emailaddress',
            unique_together=set([('user', 'email')]),
        ),
    ]
