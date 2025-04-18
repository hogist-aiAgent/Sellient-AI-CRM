# Generated by Django 5.1.5 on 2025-03-14 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_APP', '0005_alter_b2blead_contact_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='b2blead',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='b2clead',
            name='contact_number',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
