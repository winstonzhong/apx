"""apx URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

from apx import settings
import collection
from collection.views import test2

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test/', test2),
    url(r'^titleentity/(?P<tid>\d+)/$', collection.views.TitleEntityView),
    url(r'^nameentity/(?P<tid>\d+)/$', collection.views.NameEntityView),
    url(r'^htmlcontent/(?P<tid>\d+)/$', collection.views.HtmlContentView),
    url(r'^api/name_entity/$', collection.views.NameEntityAPI),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)