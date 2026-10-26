from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('eliteapp', '0010_project_manager_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='technician_hourly_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Tarif technicien / heure'),
        ),
        migrations.AddField(
            model_name='project',
            name='holiday_day_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Tarif technicien journée fériée'),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.CheckConstraint(condition=Q(('technician_hourly_rate__gte', 0)), name='positive_technician_project_rate'),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.CheckConstraint(condition=Q(('holiday_day_rate__gte', 0)), name='positive_project_holiday_rate'),
        ),
        migrations.CreateModel(
            name='PublicHoliday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Nom du jour férié')),
                ('date', models.DateField(unique=True, verbose_name='Date')),
            ],
            options={'ordering': ['date']},
        ),
    ]
