from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('eliteapp', '0014_technicianpayment'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechnicianSpecialty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True, verbose_name='Spécialité')),
            ],
            options={
                'verbose_name': 'Spécialité technicien',
                'verbose_name_plural': 'Spécialités techniciens',
                'ordering': ['name'],
            },
        ),
    ]
