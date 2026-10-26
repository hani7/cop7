from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eliteapp', '0006_user_assignment_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='rc',
            field=models.CharField(blank=True, max_length=40, verbose_name='RC'),
        ),
        migrations.AddField(
            model_name='client',
            name='nif',
            field=models.CharField(blank=True, max_length=40, verbose_name='NIF'),
        ),
        migrations.AddField(
            model_name='client',
            name='article_number',
            field=models.CharField(blank=True, max_length=40, verbose_name='N° article'),
        ),
        migrations.AddField(
            model_name='client',
            name='nis',
            field=models.CharField(blank=True, max_length=40, verbose_name='NIS'),
        ),
    ]
