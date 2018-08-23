# Generated by Django 2.1 on 2018-08-23 19:26

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContainerTaskInstance',
            fields=[
                ('name', models.CharField(blank=True, help_text='An optional non-unique name for the task instance', max_length=200, validators=[django.core.validators.RegexValidator(message=' @/+/-/_ only', regex='^[\\w@+-]+$')])),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='The UUID for the running job', primary_key=True, serialize=False, verbose_name='UUID')),
                ('state', models.CharField(choices=[('created', 'created'), ('published', 'published'), ('running', 'running'), ('successful', 'successful'), ('failed', 'failed'), ('terminated', 'terminated')], default='created', max_length=10)),
                ('datetime_created', models.DateTimeField(auto_now_add=True, help_text='When the job was created')),
                ('datetime_finished', models.DateTimeField(editable=False, help_text='When the job finished.', null=True)),
                ('arguments', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, help_text="A JSON dictionary of arguments, where the keys are the argument names and the values are their corresponding values. A task instance must specify values for all values of a task type's required arguments for which no default value exists. Defaults to {}.")),
            ],
            options={
                'ordering': ['-datetime_created'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContainerTaskType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the task', max_length=200, validators=[django.core.validators.RegexValidator(message=' @/+/-/_ only', regex='^[\\w@+-]+$')])),
                ('description', models.TextField(blank=True, help_text='A description of the task')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('command_to_run', models.CharField(help_text='The command to run to execute the task. For example, "python /app/myscript.py". Arguments will be added to the end of this command.', max_length=400)),
                ('logs_path', models.CharField(blank=True, default=None, help_text='The path of the logs directory. Specify null if no logs directory. Defaults to null.', max_length=400, null=True)),
                ('results_path', models.CharField(blank=True, default=None, help_text='The path of the results (or "outputs") directory. Specify null if no results directory. Defaults to null.', max_length=400, null=True)),
                ('environment_variables', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, help_text="A JSON array of environment variables to consume from the Celery worker's environment. Defaults to []. Note that all task instances have their job UUID available in the environment variable JOB_UUID.")),
                ('required_arguments', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, help_text='A JSON array of required argument names. Defaults to [].')),
                ('required_arguments_default_values', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, help_text='A JSON dictionary of default values for required arguments, where the keys are the argument names and the values are their corresponding default values. Defaults to {}.')),
                ('container_image', models.CharField(help_text='The container name and tag. For example, "ubuntu:14.04" for Docker; and "docker://ubuntu:14.04" or "shub://vsoch/hello-world" for Singularity.', max_length=200)),
                ('container_type', models.CharField(choices=[('docker', 'Docker'), ('singularity', 'Singularity')], help_text='The type of container provided', max_length=11)),
                ('user', models.ForeignKey(help_text='The author of this task', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaskQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Celery queue', max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message=' @/+/-/_ only', regex='^[\\w@+-]+$')])),
                ('description', models.TextField(blank=True, help_text='A description of the queue')),
                ('private', models.BooleanField(blank=True, default=False, help_text='A boolean specifying whether other users besides the queue creator can use the queue. Defaults to False.')),
                ('active', models.BooleanField(blank=True, default=True, help_text='A boolean showing the status of the queue. As of now, this needs to be toggled manually. Defaults to True.')),
                ('user', models.ForeignKey(help_text='The creator of the queue', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='containertaskinstance',
            name='task_queue',
            field=models.ForeignKey(help_text='The queue this instance runs on', on_delete=django.db.models.deletion.PROTECT, to='tasksapi.TaskQueue'),
        ),
        migrations.AddField(
            model_name='containertaskinstance',
            name='task_type',
            field=models.ForeignKey(help_text='The task type for which this is an instance', on_delete=django.db.models.deletion.PROTECT, to='tasksapi.ContainerTaskType'),
        ),
        migrations.AddField(
            model_name='containertaskinstance',
            name='user',
            field=models.ForeignKey(help_text='The author of this instance', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='containertasktype',
            unique_together={('name', 'user')},
        ),
    ]
