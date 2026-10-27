from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('eliteapp', '0013_project_access_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechnicianPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('date', models.DateField()),
                ('method', models.CharField(choices=[('TRANSFER', 'Virement'), ('CASH', 'Espèces'), ('CHECK', 'Chèque')], default='TRANSFER', max_length=12)),
                ('reference', models.CharField(blank=True, max_length=160)),
                ('note', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_technician_payments', to=settings.AUTH_USER_MODEL)),
                ('technician', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='technician_payments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date', '-id'],
            },
        ),
        migrations.AddConstraint(
            model_name='technicianpayment',
            constraint=models.CheckConstraint(condition=models.Q(('amount__gt', 0)), name='positive_technician_payment'),
        ),
    ]
