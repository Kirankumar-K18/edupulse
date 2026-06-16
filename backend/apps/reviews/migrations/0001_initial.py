from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(max_length=1000)),
                ('semester', models.PositiveSmallIntegerField()),
                ('academic_year', models.CharField(max_length=9)),
                ('is_blocked', models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='accounts.student')),
                ('lecturer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='accounts.lecturer')),
            ],
            options={'ordering': ['-submitted_at'], 'unique_together': {('student', 'lecturer', 'semester', 'academic_year')}},
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['lecturer', 'is_blocked'], name='reviews_lecturer_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['student', '-submitted_at'], name='reviews_student_idx'),
        ),
        migrations.CreateModel(
            name='BlockedReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blocked_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField()),
                ('matched_words', models.JSONField(default=list)),
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='block_record', to='reviews.review')),
            ],
            options={'ordering': ['-blocked_at']},
        ),
    ]
