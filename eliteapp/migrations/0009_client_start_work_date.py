from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eliteapp', '0008_client_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='start_work_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date de début de travail'),
        ),
    ]
