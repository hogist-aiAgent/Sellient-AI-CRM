# Generated by Django 5.1.5 on 2025-04-02 08:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_APP', '0020_b2blead_lead_status_b2clead_lead_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inpersonlead',
            name='source_comefrom',
        ),
        migrations.AddField(
            model_name='b2blead',
            name='from_inperson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='food_APP.inpersonlead'),
        ),
        migrations.AddField(
            model_name='b2blead',
            name='from_outsource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='food_APP.outsorcedblead'),
        ),
        migrations.AddField(
            model_name='b2blead',
            name='lead_generater_name',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='b2blead',
            name='remark',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='b2clead',
            name='remark',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inpersonlead',
            name='source_come_from',
            field=models.CharField(default='Sales_person', max_length=225),
        ),
        migrations.AddField(
            model_name='outsorcedblead',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='outsorcedblead',
            name='source_come_from',
            field=models.CharField(default='PDataBase', max_length=225),
        ),
    ]
