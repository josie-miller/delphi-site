"""
URL configuration for delphi_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('blog/<int:post_id>/like/', views.like_post, name='like_post'),
    path('prediction-market/', views.prediction_market, name='prediction_market'),  # Ensure the URL is correct
    path('submit-answer/', views.submit_answer, name='submit_answer'),  # For AJAX submission
    path('get_climate_factors/', views.get_climate_factors, name='get_climate_factors'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)