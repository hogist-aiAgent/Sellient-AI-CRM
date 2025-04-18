# Generated by Django 5.1.5 on 2025-03-13 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food_APP', '0003_b2bfollowup_b2cfollowup_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='b2blead',
            old_name='delivary_location',
            new_name='delivery_location',
        ),
        migrations.AlterField(
            model_name='b2bfollowup',
            name='followup_status',
            field=models.CharField(choices=[('meeting_scheduled', 'Meeting Scheduled'), ('meeting_done', 'Meeting Done'), ('process_hold', 'Process Hold'), ('process_further', 'Process Further'), ('process_finished', 'Process Finished'), ('kitchen_visit_done', 'Kitchen Visit Done'), ('sampling_done', 'Sampling Done'), ('finalized', 'Finalized'), ('date_confirmed', 'Date Confirmed'), ('customer', 'Converted to Customer')], default='meeting_done', max_length=50),
        ),
        migrations.AlterField(
            model_name='b2blead',
            name='status',
            field=models.CharField(choices=[('Meeting Scheduled', 'Meeting Scheduled'), ('Meeting not Scheduled', 'Meeting not Scheduled'), ('Not Interested', 'Not Inte')], max_length=50),
        ),
    ]
