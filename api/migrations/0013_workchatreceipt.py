from django.db import migrations, models
import django.db.models.deletion
import uuid
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('science_publishing', '0012_rename_science_pub_profile_ye_cf2703_idx_science_pub_profile_6cc95d_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkChatReceipt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('delivered_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Доставлено')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='Прочитано')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='science_publishing.workchatmessage', verbose_name='Сообщение')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='science_publishing_chat_receipts', to=settings.AUTH_USER_MODEL, verbose_name='Получатель')),
            ],
            options={
                'verbose_name': 'Статус сообщения',
                'verbose_name_plural': 'Статусы сообщений',
            },
        ),
        migrations.AddIndex(
            model_name='workchatreceipt',
            index=models.Index(fields=['recipient', 'read_at'], name='science_pub_recipient_idx'),
        ),
        migrations.AddIndex(
            model_name='workchatreceipt',
            index=models.Index(fields=['message', 'recipient'], name='science_pub_message__idx'),
        ),
        migrations.AlterUniqueTogether(
            name='workchatreceipt',
            unique_together={('message', 'recipient')},
        ),
    ]
