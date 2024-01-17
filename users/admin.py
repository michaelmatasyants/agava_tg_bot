from django.contrib import admin

from users.models import TgUser


class TgUserAdminInline(admin.TabularInline):
    model = TgUser.friends.through
    fk_name = 'from_tguser'
    verbose_name = 'Кого пригласил'
    verbose_name_plural = 'Кого пригласил'

@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'tg_id', 'joined_agava_crypto',
                    'joined_squad', 'got_free_dep']
    inlines = [TgUserAdminInline, ]
    fieldsets = (
        ('О пользователе', {
            'fields': ['nickname', 'tg_id'],
        }),
        ('Выполненные задания', {
            'fields': ['joined_agava_crypto', 'joined_squad', 'got_free_dep']
        }),
    )
