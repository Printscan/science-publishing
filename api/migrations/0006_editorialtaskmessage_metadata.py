from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('science_publishing', '0005_alter_editorialrole_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='editorialtaskmessage',
            name='metadata',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Структурированные сведения об изменениях, вложениях и прочем контексте.',
                verbose_name='Дополнительные данные',
            ),
        ),
        migrations.AddField(
            model_name='editorialtaskmessage',
            name='is_system',
            field=models.BooleanField(
                default=False,
                help_text='Помечает автоматические системные сообщения.',
                verbose_name='Системное сообщение',
            ),
        ),
    ]
