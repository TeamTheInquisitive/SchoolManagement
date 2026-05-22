from django.utils.deprecation import MiddlewareMixin
from apps.core.models import School


class TenantMiddleware(MiddlewareMixin):
    """Extract tenant (school) from request header or subdomain."""

    def process_request(self, request):
        # Try X-School-Code header first, then subdomain
        school_code = request.headers.get('X-School-Code', '')
        if not school_code:
            host = request.get_host().split(':')[0]
            parts = host.split('.')
            if len(parts) > 2:
                school_code = parts[0]

        request.school = None
        if school_code:
            try:
                request.school = School.objects.get(code=school_code, is_active=True)
            except School.DoesNotExist:
                pass
