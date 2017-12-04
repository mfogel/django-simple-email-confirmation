# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()
user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.module_name)


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailAddress'
        db.create_table('simple_email_confirmation_emailaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='email_address_set', to=orm[user_orm_label])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('set_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('confirmed_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('simple_email_confirmation', ['EmailAddress'])

        # Adding unique constraint on 'EmailAddress', fields ['user', 'email']
        db.create_unique('simple_email_confirmation_emailaddress', ['user_id', 'email'])


    def backwards(self, orm):
        # Removing unique constraint on 'EmailAddress', fields ['user', 'email']
        db.delete_unique('simple_email_confirmation_emailaddress', ['user_id', 'email'])

        # Deleting model 'EmailAddress'
        db.delete_table('simple_email_confirmation_emailaddress')


    models = {
        'simple_email_confirmation.emailaddress': {
            'Meta': {'unique_together': "(('user', 'email'),)", 'object_name': 'EmailAddress'},
            'confirmed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'set_at': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_address_set'", 'to': "orm['%s']" % user_orm_label, 'on_delete': models.CASCADE})
        },
        user_model_label: {
        },
    }

    complete_apps = ['simple_email_confirmation']
