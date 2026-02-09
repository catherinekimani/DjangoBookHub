# Generated manually to handle Book model restructuring

from django.db import migrations, models
import cloudinary.models


class Migration(migrations.Migration):

    dependencies = [
        ('BookManager', '0006_book_file_url_book_info_link'),
    ]

    operations = [
        # Remove old fields that no longer exist
        migrations.RemoveField(
            model_name='book',
            name='price',
        ),
        migrations.RemoveField(
            model_name='book',
            name='stock_quantity',
        ),
        migrations.RemoveField(
            model_name='book',
            name='book_pages',
        ),
        migrations.RemoveField(
            model_name='book',
            name='total_review',
        ),
        migrations.RemoveField(
            model_name='book',
            name='total_rating',
        ),
        migrations.RemoveField(
            model_name='book',
            name='status',
        ),
        # Change cover_image from CloudinaryField to URLField
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=models.URLField(blank=True, help_text='Google Books thumbnail URL'),
        ),
        # Update title and slug max_length
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='book',
            name='slug',
            field=models.SlugField(max_length=220),
        ),
        # Make description optional
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.TextField(blank=True),
        ),
        # Add new fields
        migrations.AddField(
            model_name='book',
            name='authors',
            field=models.CharField(blank=True, help_text='Comma-separated author names', max_length=300),
        ),
        migrations.AddField(
            model_name='book',
            name='published_date',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='book',
            name='google_books_id',
            field=models.CharField(blank=True, help_text='Google Books volume ID', max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='book',
            name='preview_link',
            field=models.URLField(blank=True, help_text='Preview/read link if available'),
        ),
        migrations.AddField(
            model_name='book',
            name='local_file',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='book_files'),
        ),
        migrations.AddField(
            model_name='book',
            name='page_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='categories',
            field=models.CharField(blank=True, help_text='Google Books categories', max_length=300),
        ),
        migrations.AddField(
            model_name='book',
            name='is_curated',
            field=models.BooleanField(default=False, help_text='Manually reviewed and approved'),
        ),
        migrations.AddField(
            model_name='book',
            name='is_featured',
            field=models.BooleanField(default=False, help_text='Show on homepage'),
        ),
        migrations.AddField(
            model_name='book',
            name='view_count',
            field=models.IntegerField(default=0),
        ),
    ]


