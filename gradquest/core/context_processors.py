from .models import SiteSetting

def pyq_context(request):
    return {
        'pyq_link': SiteSetting.get_pyq_link()
    }
