from django.db import migrations, models
import django.db.models.deletion


def copy_manager_names(apps, schema_editor):
    Project = apps.get_model('eliteapp', 'Project')
    for project in Project.objects.select_related('project_manager').iterator():
        manager = project.project_manager
        project.manager_name = (
            f'{manager.first_name} {manager.last_name}'.strip()
            or manager.username
        )
        project.save(update_fields=['manager_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('eliteapp', '0009_client_start_work_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='manager_name',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Chef de projet client'),
        ),
        migrations.RunPython(copy_manager_names, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='project',
            name='project_manager',
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={'role': 'PROJECT_MANAGER'},
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='managed_projects',
                to='eliteapp.user',
            ),
        ),
    ]
