from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class ItechsPermissionMixin(LoginRequiredMixin, UserPassesTestMixin):
    redirect_field_name = 'redirect_to'

    def test_func(self):
        from account.models import ItechsPermission
        try:
            itechs_permissions = ItechsPermission.objects.get(user=self.request.user)
        except ItechsPermission.DoesNotExist:
            return False
        else:
            return itechs_permissions.is_active

    def get_login_url(self):
        if self.request.user.is_authenticated:
            if self.test_func():
                return '/dashboard/'
        return super().get_login_url()


class CpInspectionPermissionMixin(ItechsPermissionMixin):

    def test_func(self):
        from account.models import ItechsPermission
        try:
            itechs_permissions = ItechsPermission.objects.get(user=self.request.user)
        except ItechsPermission.DoesNotExist:
            return False
        else:
            if itechs_permissions.is_active is True:
                return any([itechs_permissions.cp_inspection, itechs_permissions.cp_inspection_admin])
            else:
                return False


class CpInspectionSummaryPermissionMixin(ItechsPermissionMixin):

    def test_func(self):
        from account.models import ItechsPermission
        try:
            itechs_permissions = ItechsPermission.objects.get(user=self.request.user)
        except ItechsPermission.DoesNotExist:
            return False
        else:
            if itechs_permissions.is_active is True:
                return any([itechs_permissions.cp_inspection_summary, itechs_permissions.cp_inspection_admin])
            else:
                return False


class CpInspectionAdminPermissionMixin(ItechsPermissionMixin):

    def test_func(self):
        from account.models import ItechsPermission
        try:
            itechs_permissions = ItechsPermission.objects.get(user=self.request.user)
        except ItechsPermission.DoesNotExist:
            return False
        else:
            return all([itechs_permissions.is_active, itechs_permissions.cp_inspection_admin])
