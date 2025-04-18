# Generated by Django 5.1.5 on 2025-03-14 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_APP', '0004_rename_delivary_location_b2blead_delivery_location_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='b2blead',
            name='contact_number',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='dietary_options',
            field=models.CharField(choices=[('Veg', 'Veg'), ('Non_Veg', 'Non_Veg'), ('Vegan', 'Vegan')], default='Unknown', max_length=50),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='status',
            field=models.CharField(choices=[('Meeting Scheduled', 'Meeting Scheduled'), ('Meeting not Scheduled', 'Meeting not Scheduled'), ('Not Interested', 'Not Interested')], max_length=50),
        ),
        migrations.AlterField(
            model_name='b2clead',
            name='dietary_options',
            field=models.CharField(choices=[('Veg', 'Veg'), ('Non_Veg', 'Non_Veg'), ('Vegan', 'Vegan')], default='Unknown', max_length=50),
        ),
    ]
