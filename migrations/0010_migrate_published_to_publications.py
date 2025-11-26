from django.db import migrations


def migrate_published_to_publications(apps, schema_editor):
    Work = apps.get_model('science_publishing', 'Work')
    Publication = apps.get_model('science_publishing', 'Publication')

    for work in Work.objects.filter(status='published'):
        Publication.objects.update_or_create(
            source_work=work,
            defaults={
                'profile': work.profile,
                'author_full_name': work.author_full_name,
                'publication_kind': work.publication_kind,
                'guideline_subtype': work.guideline_subtype,
                'discipline_name': work.discipline_name,
                'discipline_topic': work.discipline_topic,
                'rector_name': work.rector_name,
                'year': work.year,
                'pages_count': work.pages_count,
                'udc': work.udc,
                'bbk': work.bbk,
                'developers': work.developers,
                'scientific_editor': work.scientific_editor,
                'computer_layout': work.computer_layout,
                'co_authors': work.co_authors,
                'training_form': work.training_form,
                'faculty': work.faculty,
                'department': work.department,
                'short_description': work.short_description,
                'document': work.document,
                'status': work.status,
                'current_editor': work.current_editor,
                'published_at': work.published_at,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('science_publishing', '0009_publication'),
    ]

    operations = [
        migrations.RunPython(migrate_published_to_publications, migrations.RunPython.noop),
    ]

