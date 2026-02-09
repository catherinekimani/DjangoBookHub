# Generated manually to add Theme and related models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.utils.text


def create_slugs(apps, schema_editor):
    """Create slugs for existing Theme objects if any."""
    Theme = apps.get_model('BookManager', 'Theme')
    for theme in Theme.objects.all():
        if not theme.slug:
            theme.slug = django.utils.text.slugify(theme.name)
            theme.save()


class Migration(migrations.Migration):

    dependencies = [
        ('BookManager', '0007_update_book_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('tagline', models.CharField(help_text="Short, compelling hook (e.g., 'Making sense of AI disruption')", max_length=200)),
                ('why_now', models.TextField(help_text='Explain why this theme matters right now - contextual, urgent, human')),
                ('icon', models.CharField(blank=True, help_text="Emoji or icon class (e.g., 'fa-brain')", max_length=50)),
                ('order', models.IntegerField(default=0, help_text='Display order on homepage')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Theme',
                'verbose_name_plural': 'Themes',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='BookThemedAssociation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contextual_note', models.TextField(help_text='Why is THIS book relevant to THIS theme RIGHT NOW? Be specific, human, and insightful.')),
                ('curator_pick', models.BooleanField(default=False, help_text="Highlight as a 'Curator's Pick'")),
                ('order', models.IntegerField(default=0, help_text='Order within the theme')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='theme_associations', to='BookManager.book')),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_associations', to='BookManager.theme')),
            ],
            options={
                'verbose_name': 'Book-Theme Association',
                'verbose_name_plural': 'Book-Theme Associations',
                'ordering': ['order', '-created'],
                'unique_together': {('book', 'theme')},
            },
        ),
        migrations.CreateModel(
            name='ReadingNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField()),
                ('is_public', models.BooleanField(default=False, help_text='Share with community')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_notes', to='BookManager.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reading_notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reading Note',
                'verbose_name_plural': 'Reading Notes',
                'ordering': ['-created'],
            },
        ),
        migrations.RunPython(create_slugs, migrations.RunPython.noop),
    ]


