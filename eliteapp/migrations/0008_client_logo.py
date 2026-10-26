from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eliteapp', '0007_client_registration_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='logo',
            field=models.FileField(blank=True, upload_to='client-logos/', verbose_name='Logo'),
        ),
    ]
