from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('eliteapp', '0015_technicianspecialty'),
    ]

    operations = [
        migrations.AddField('client', 'deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
        migrations.AddField('user', 'deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
        migrations.AddField('project', 'deleted_at', models.DateTimeField(blank=True, db_index=True, null=True)),
    ]
