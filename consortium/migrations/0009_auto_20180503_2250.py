# Generated by Django 2.0.2 on 2018-05-03 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consortium', '0008_auto_20180503_1837'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='time_step',
            new_name='work_step',
        ),
        migrations.RemoveField(
            model_name='company',
            name='active',
        ),
        migrations.RemoveField(
            model_name='company',
            name='alt_contact_phone',
        ),
        migrations.RemoveField(
            model_name='company',
            name='contact_phone',
        ),
        migrations.RemoveField(
            model_name='company',
            name='spouse_name',
        ),
        migrations.AddField(
            model_name='company',
            name='appt_step',
            field=models.PositiveIntegerField(default=30, verbose_name='Appointment Select Time Step'),
        ),
        migrations.AlterField(
            model_name='company',
            name='city',
            field=models.CharField(max_length=100, verbose_name='city'),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_phone',
            field=models.CharField(default=2223334444, max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='company',
            name='email',
            field=models.EmailField(default=1, max_length=254, verbose_name='contact email address'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='company',
            name='owner',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='company owner'),
        ),
        migrations.AlterField(
            model_name='company',
            name='street_address',
            field=models.CharField(max_length=100, verbose_name='street'),
        ),
    ]
