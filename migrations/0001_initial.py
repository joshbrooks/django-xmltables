# Generated by Django 2.2.7 on 2019-11-29 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='XmlColumn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('col_name', models.CharField(max_length=256)),
                ('col_type', models.CharField(default='text', max_length=256)),
                ('column_expression', models.CharField(blank=True, max_length=256, null=True)),
                ('default_expression', models.CharField(blank=True, max_length=256, null=True)),
                ('not_null', models.BooleanField(default=False)),
                ('for_ordinality', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='XmlNamespace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='XmlTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_expression', models.CharField(max_length=256)),
                ('row_expression', models.CharField(max_length=256)),
                ('columns', models.ManyToManyField(to='xmltables.XmlColumn')),
                ('namespaces', models.ManyToManyField(to='xmltables.XmlNamespace')),
            ],
        ),
    ]
