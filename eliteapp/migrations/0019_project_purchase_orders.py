from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('eliteapp', '0018_project_purchase_order_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='purchase_orders',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
