from django.contrib import admin

from users.models import TgUser


@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'tg_id', 'joined_agava_crypto',
                    'joined_squad', 'got_free_dep']
