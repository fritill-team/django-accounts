# Generated by Django 3.2.8 on 2023-02-01 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='siteprofile',
            options={'default_permissions': (), 'verbose_name': 'Site Profile', 'verbose_name_plural': 'Sites Profiles'},
        ),
    ]
