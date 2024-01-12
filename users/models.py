from django.db import models


class TgUser(models.Model):
    nickname = models.CharField('Никнейм',
                                max_length=20)
    tg_id = models.IntegerField('ID_пользователя')
    joined_agava_crypto = models.BooleanField('Подписался на канал',
                                              default=False)
    joined_squad = models.BooleanField('Присоединился к скваду',
                                       default=False)
    got_free_dep = models.BooleanField('Переход в казино',
                                       default=False)

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
