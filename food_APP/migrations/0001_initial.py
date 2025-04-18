# Generated by Django 3.2.25 on 2025-03-07 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='B2BLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=15)),
                ('alternate_number', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('event_type', models.CharField(choices=[('Industrial', 'Industrial'), ('Corporate', 'Corporate')], max_length=50)),
                ('company_name', models.CharField(max_length=255)),
                ('designation', models.CharField(max_length=255)),
                ('delivary_location', models.TextField()),
                ('count', models.IntegerField(default=50)),
                ('required_meal_service', models.CharField(choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Dinner', 'Dinner'), ('Tea & Snacks', 'Tea & Snacks'), ('Supper', 'Supper'), ('All', 'All')], max_length=50)),
                ('service_type', models.CharField(choices=[('In_house', 'In_house'), ('Outsource', 'Outsource')], max_length=50)),
                ('service_choice', models.CharField(choices=[('Just delivery', 'Just delivery'), ('Buffet', 'Buffet'), ('With Service Person', 'With Service Person')], max_length=50)),
                ('choice_of_menu', models.TextField(blank=True, max_length=200, null=True)),
                ('existing_menu_budget', models.CharField(blank=True, max_length=50, null=True)),
                ('prefered_menu_budget', models.CharField(blank=True, max_length=50, null=True)),
                ('meeting_date_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('Menu & Price Fixed', 'Menu & Price Fixed'), ('Meeting Scheduled', 'Meeting Scheduled'), ('Kitchen Visit', 'Kitchen Visit'), ('Client Visit', 'Client Visit'), ('Sampling', 'Sampling'), ('Start date confirmed', 'Start date confirmed')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='B2CLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=15)),
                ('alternate_number', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('event_type', models.CharField(max_length=255)),
                ('event_date_time', models.DateTimeField()),
                ('delivery_location', models.TextField()),
                ('count', models.IntegerField(default=50)),
                ('required_model_service', models.CharField(choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Dinner', 'Dinner'), ('Snacks', 'Snacks'), ('Hi_tea', 'Hi_tea')], max_length=50)),
                ('service_choice', models.CharField(choices=[('Just delivery', 'Just delivery'), ('Buffet', 'Buffet'), ('With Service Person', 'With Service Person')], max_length=50)),
                ('choice_of_menu', models.TextField(blank=True, max_length=200, null=True)),
                ('existing_menu_budget', models.CharField(blank=True, max_length=50, null=True)),
                ('prefered_menu_budget', models.CharField(blank=True, max_length=50, null=True)),
                ('meeting_date_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('Menu & Price Fixed', 'Menu & Price Fixed'), ('Payment', 'Payment'), ('Start date confirmed', 'Start date confirmed')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
