# Generated by Django 5.1.5 on 2025-04-11 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_APP', '0022_b2clead_from_inperson_b2clead_from_outsource_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outsorcedblead',
            name='status',
            field=models.CharField(max_length=255),
        ),
    ]
