from ckeditor.fields import RichTextField
from django.db import models

from commons.models import DateTimeMixin


class Notice(DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '공지사항'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    title = models.CharField(max_length=300, null=False, blank=False, verbose_name='제목')
    is_open = models.BooleanField(default=True, blank=False, null=False, verbose_name='노출')
    body = RichTextField(null=False, blank=False, verbose_name='본문')


class NoticeReadLog(DateTimeMixin, models.Model):
    account = models.OneToOneField('account.User', null=False, blank=False, verbose_name='사용자', on_delete=models.PROTECT)
    notice = models.ForeignKey(Notice, null=False, blank=False, verbose_name='공지사항', on_delete=models.PROTECT)
