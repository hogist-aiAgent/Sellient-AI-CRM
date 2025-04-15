# Generated by Django 5.1.5 on 2025-04-07 10:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_APP', '0021_remove_inpersonlead_source_comefrom_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='b2clead',
            name='from_inperson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='b2c_from_inperson', to='food_APP.inpersonlead'),
        ),
        migrations.AddField(
            model_name='b2clead',
            name='from_outsource',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='food_APP.outsorcedblead'),
        ),
        migrations.AddField(
            model_name='b2clead',
            name='lead_generater_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='b2c_generated_by', to='food_APP.inpersonlead'),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='from_inperson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='b2b_from_inperson', to='food_APP.inpersonlead'),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='lead_generater_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='b2b_generated_by', to='food_APP.inpersonlead'),
        ),
        migrations.AlterField(
            model_name='outsorcedblead',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
