from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('semester', models.PositiveSmallIntegerField(default=1)),
                ('credits', models.PositiveSmallIntegerField(default=3)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='accounts.department')),
                ('lecturer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subjects', to='accounts.lecturer')),
            ],
            options={'ordering': ['name'], 'unique_together': {('code', 'department')}},
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('present','Present'),('absent','Absent'),('late','Late')], default='present', max_length=10)),
                ('remarks', models.CharField(blank=True, max_length=200)),
                ('marked_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='accounts.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='attendance.subject')),
                ('lecturer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_records', to='accounts.lecturer')),
            ],
            options={'ordering': ['-date'], 'unique_together': {('student', 'subject', 'date')}},
        ),
        migrations.AddIndex(
            model_name='attendancerecord',
            index=models.Index(fields=['student', 'subject'], name='attendance_student_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecord',
            index=models.Index(fields=['lecturer', 'date'], name='attendance_lecturer_idx'),
        ),
    ]
