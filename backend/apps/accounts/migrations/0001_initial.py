from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('full_name', models.CharField(max_length=150)),
                ('role', models.CharField(choices=[('admin','Admin'),('hod','HOD'),('lecturer','Lecturer'),('student','Student')], max_length=20)),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profiles/')),
            ],
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usn', models.CharField(max_length=20, unique=True, verbose_name='USN')),
                ('section', models.CharField(max_length=5)),
                ('semester', models.PositiveSmallIntegerField(default=1)),
                ('batch_year', models.PositiveIntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to='accounts.user')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='students', to='accounts.department')),
            ],
            options={'ordering': ['usn']},
        ),
        migrations.CreateModel(
            name='Lecturer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(max_length=20, unique=True)),
                ('designation', models.CharField(default='Assistant Professor', max_length=100)),
                ('qualification', models.CharField(blank=True, max_length=200)),
                ('experience_years', models.PositiveSmallIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='lecturer_profile', to='accounts.user')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lecturers', to='accounts.department')),
            ],
            options={'ordering': ['user__full_name']},
        ),
        migrations.CreateModel(
            name='HOD',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('joined_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='hod_profile', to='accounts.user')),
                ('department', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='hod', to='accounts.department')),
            ],
            options={'verbose_name': 'HOD'},
        ),
        migrations.CreateModel(
            name='BadWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bad_words_added', to='accounts.user')),
            ],
            options={'ordering': ['word']},
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login','Login'),('logout','Logout'),('login_failed','Login Failed'),('attendance','Attendance Marked'),('review','Review Submitted'),('review_blocked','Review Blocked'),('user_created','User Created'),('user_deleted','User Deleted'),('user_updated','User Updated'),('dept_created','Department Created'),('dept_updated','Department Updated'),('arq_event','ARQ Protocol Event'),('badword_added','Bad Word Added'),('password_change','Password Changed')], max_length=30)),
                ('description', models.TextField()),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('extra_data', models.JSONField(blank=True, default=dict)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_success', models.BooleanField(default=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activity_logs', to='accounts.user')),
            ],
            options={'ordering': ['-timestamp']},
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['action', '-timestamp'], name='accounts_ac_action_idx'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['user', '-timestamp'], name='accounts_ac_user_idx'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='accounts_user_groups', to='auth.group'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, related_name='accounts_user_permissions', to='auth.permission'),
        ),
    ]
