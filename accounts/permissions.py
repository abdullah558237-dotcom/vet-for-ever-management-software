from django.contrib.auth.mixins import UserPassesTestMixin


class RoleRequiredMixin(UserPassesTestMixin):
    """Usage: class MyView(RoleRequiredMixin, ListView): allowed_roles = ['admin', 'vet']"""
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser or user.role in self.allowed_roles
        )
