from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('science_publishing', '0007_alter_editorialtaskmessage_is_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='editorialtask',
            name='closed_at',
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name='��� �������',
            ),
        ),
        migrations.AddField(
            model_name='editorialtask',
            name='payload',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='��⠫� ��।��, ��������, ���������.',
                verbose_name='�������⥫�� �����',
            ),
        ),
        migrations.AddField(
            model_name='editorialtask',
            name='previous_task',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name='next_task',
                to='science_publishing.editorialtask',
                verbose_name='�।���� �����',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='editorialtask',
            unique_together=set(),
        ),
    ]

