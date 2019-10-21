# Generated by Django 2.0.2 on 2018-05-03 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consortium', '0007_hours_time_step'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hours',
            name='time_step',
        ),
        migrations.AddField(
            model_name='company',
            name='time_step',
            field=models.PositiveIntegerField(default=30, verbose_name='Schedule Select Time Step'),
        ),
        migrations.AlterField(
            model_name='hours',
            name='closed',
            field=models.BooleanField(default=False, verbose_name='Closed on this day'),
        ),
    ]