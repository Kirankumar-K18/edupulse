from django.contrib import admin
from .models import ARQSession, ARQEvent

class ARQEventInline(admin.TabularInline):
    model = ARQEvent
    extra = 0
    readonly_fields = ['event_type', 'packet_number', 'attempt', 'message', 'timestamp_ms']

@admin.register(ARQSession)
class ARQSessionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'total_packets', 'packets_sent_ok',
                    'total_transmissions', 'status', 'created_at']
    list_filter  = ['status']
    inlines      = [ARQEventInline]
