# Generated by Django 5.1.5 on 2025-03-17 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_APP', '0006_alter_b2blead_email_alter_b2clead_contact_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='b2blead',
            name='company_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='count',
            field=models.IntegerField(blank=True, default=50, null=True),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='delivery_location',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='designation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
