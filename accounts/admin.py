from django.contrib import admin
from .models import NewsletterSubscription
from django.utils.html import format_html
from django.utils import timezone

class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'email', 
        'is_subscribed_display', 
        'confirmed_at_display',
        'subscribed_at_display', 
        'user_display',
        'created_at_display',
        'days_since_subscription'
    )
    
    list_filter = (
        'is_subscribed', 
        'confirmed_at',
        'subscribed_at',
        'created_at'
    )
    
    search_fields = ('email', 'user__email', 'user__username')
    
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Subscription Information', {
            'fields': (
                'email', 
                'user', 
                'is_subscribed',
                'confirmed_at',
                'subscribed_at',
                'unsubscribed_at'
            )
        }),
        ('Confirmation Details', {
            'fields': (
                'confirmation_token',
                'created_at',
                'updated_at'
            )
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['mark_as_subscribed', 'mark_as_unsubscribed', 'delete_selected']
    
    def is_subscribed_display(self, obj):
        """Display subscription status with colored badges"""
        if obj.is_subscribed and obj.confirmed_at:
            color = 'green'
            status = '✅ Subscribed'
        elif obj.is_subscribed and not obj.confirmed_at:
            color = 'orange'
            status = '🔄 Pending Confirmation'
        else:
            color = 'red'
            status = '❌ Unsubscribed'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    is_subscribed_display.short_description = 'Status'
    is_subscribed_display.admin_order_field = 'is_subscribed'
    
    def confirmed_at_display(self, obj):
        """Display confirmation date"""
        if obj.confirmed_at:
            return obj.confirmed_at.strftime('%Y-%m-%d %H:%M')
        return '—'
    confirmed_at_display.short_description = 'Confirmed'
    confirmed_at_display.admin_order_field = 'confirmed_at'
    
    def subscribed_at_display(self, obj):
        """Display subscription date"""
        if obj.subscribed_at:
            return obj.subscribed_at.strftime('%Y-%m-%d %H:%M')
        return '—'
    subscribed_at_display.short_description = 'Subscribed'
    subscribed_at_display.admin_order_field = 'subscribed_at'
    
    def created_at_display(self, obj):
        """Display creation date"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'
    
    def user_display(self, obj):
        """Display associated user"""
        if obj.user:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.user.id,
                obj.user.email or obj.user.username
            )
        return '—'
    user_display.short_description = 'User'
    
    def days_since_subscription(self, obj):
        """Calculate days since subscription"""
        if obj.subscribed_at:
            days = (timezone.now() - obj.subscribed_at).days
            return f"{days} days"
        return '—'
    days_since_subscription.short_description = 'Age'
    
    def mark_as_subscribed(self, request, queryset):
        """Bulk mark selected subscriptions as subscribed"""
        updated = queryset.update(
            is_subscribed=True,
            confirmed_at=timezone.now(),
            subscribed_at=timezone.now()
        )
        self.message_user(request, f'{updated} subscriptions marked as subscribed.')
    mark_as_subscribed.short_description = 'Mark selected as subscribed'
    
    def mark_as_unsubscribed(self, request, queryset):
        """Bulk mark selected subscriptions as unsubscribed"""
        updated = queryset.update(
            is_subscribed=False,
            unsubscribed_at=timezone.now()
        )
        self.message_user(request, f'{updated} subscriptions marked as unsubscribed.')
    mark_as_unsubscribed.short_description = 'Mark selected as unsubscribed'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        total = NewsletterSubscription.objects.count()
        confirmed = NewsletterSubscription.objects.filter(
            is_subscribed=True, 
            confirmed_at__isnull=False
        ).count()
        pending = NewsletterSubscription.objects.filter(
            is_subscribed=False, 
            confirmation_token__isnull=False
        ).count()
        unsubscribed = NewsletterSubscription.objects.filter(
            is_subscribed=False, 
            confirmed_at__isnull=True
        ).count()
        
        extra_context['total_subscribers'] = total
        extra_context['confirmed_subscribers'] = confirmed
        extra_context['pending_subscribers'] = pending
        extra_context['unsubscribed'] = unsubscribed
        
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(NewsletterSubscription, NewsletterSubscriptionAdmin)