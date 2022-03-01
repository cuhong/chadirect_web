from django.contrib import admin, messages
from inline_actions.admin import InlineActionsModelAdminMixin

from car_cms.models import Notice, Message


@admin.register(Notice)
class NoticeAdmin(InlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'is_open', 'registered_at']
    list_filter = ['is_open']
    search_fields = ['title__icontains', 'body__icontains']

    def get_inline_actions(self, request, obj=None):
        actions = super(NoticeAdmin, self).get_inline_actions(request, obj)
        if obj:
            actions.append('_toggle')
        return actions

    def _toggle(self, request, obj, parent_obj=None):
        current_status = obj.is_open
        obj.is_open = True if current_status is False else False
        obj.save()
        if current_status is True:
            messages.success(request, '공지가 비공개 처리 되었습니다.')
        else:
            messages.success(request, '공지가 공개 처리 되었습니다.')

    _toggle.short_description = '공개상태 변경'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass