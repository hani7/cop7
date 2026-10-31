from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('eliteapp', '0016_soft_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='mission_expenses',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
