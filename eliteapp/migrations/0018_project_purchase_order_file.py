from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('eliteapp', '0017_project_mission_expenses'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='purchase_order_file',
            field=models.FileField(blank=True, upload_to='purchase-orders/'),
        ),
    ]
