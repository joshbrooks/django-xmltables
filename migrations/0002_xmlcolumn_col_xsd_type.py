# Generated by Django 3.0 on 2019-12-09 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xmltables', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='xmlcolumn',
            name='col_xsd_type',
            field=models.CharField(default='xsd:string', max_length=256),
        ),
    ]