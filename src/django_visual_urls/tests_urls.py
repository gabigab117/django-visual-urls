from django.urls import path, include
from django.contrib import admin
from django.http import HttpResponse

def home(request):
    return HttpResponse("Home")

def about(request):
    return HttpResponse("About")

def api_list(request):
    return HttpResponse("API List")

def api_detail(request, pk):
    return HttpResponse(f"API Detail {pk}")

def sub_view(request):
    return HttpResponse("Sub View")

# Sous-patterns pour tester l'include/récursivité
sub_patterns = [
    path('test/', sub_view, name='sub_view'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('api/', api_list, name='api_list'),
    path('api/<int:pk>/', api_detail, name='api_detail'),
    # Test de la récursivité
    path('nested/', include(sub_patterns)),
]
