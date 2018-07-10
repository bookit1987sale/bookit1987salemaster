# Generated by Django 2.0.2 on 2018-06-01 22:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffer', '0009_auto_20180515_2228'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailabilityForDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, max_length=150)),
                ('origin', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('day', models.CharField(max_length=15, verbose_name='Day of the week')),
                ('scheduled_start', models.CharField(max_length=15, verbose_name='start time of day')),
                ('scheduled_end', models.CharField(max_length=15, verbose_name='end time of day')),
                ('staff_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_availability', to='staffer.StaffMember', verbose_name='Staff Member')),
            ],
            options={
                'verbose_name': "Staff's Scheduled Hours For Day Of The Week",
                'verbose_name_plural': "Staff's Scheduled Hours For Days Of The Week",
                'ordering': ['day', 'staff_member'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='availabilityforday',
            unique_together={('staff_member', 'day')},
        ),
    ]
