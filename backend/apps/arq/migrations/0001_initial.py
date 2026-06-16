from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ARQSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_packets', models.PositiveSmallIntegerField(default=5)),
                ('loss_probability', models.FloatField(default=0.2)),
                ('timeout_seconds', models.FloatField(default=2.0)),
                ('max_retries', models.PositiveSmallIntegerField(default=3)),
                ('status', models.CharField(choices=[('running','Running'),('completed','Completed'),('failed','Failed')], default='running', max_length=15)),
                ('packets_sent_ok', models.PositiveSmallIntegerField(default=0)),
                ('total_transmissions', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arq_sessions', to='accounts.user')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ARQEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('send','Packet Sent'),('ack','ACK Received'),('timeout','Timeout'),('retransmit','Retransmission'),('drop','Packet Dropped (Simulated Loss)'),('success','Packet Delivered')], max_length=15)),
                ('packet_number', models.PositiveSmallIntegerField()),
                ('attempt', models.PositiveSmallIntegerField(default=1)),
                ('message', models.CharField(max_length=300)),
                ('timestamp_ms', models.IntegerField(default=0)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='arq.arqsession')),
            ],
            options={'ordering': ['timestamp_ms', 'pk']},
        ),
    ]
