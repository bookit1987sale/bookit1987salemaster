# Generated by Django 2.0.2 on 2018-06-07 23:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0030_auto_20180607_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientevent',
            name='second_event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='staff_for_client_second_event', to='event.SecondPartEvent', verbose_name='Second Part Event'),
        ),
    ]