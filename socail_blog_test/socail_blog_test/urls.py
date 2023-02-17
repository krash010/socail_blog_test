from django.contrib import admin
from django.urls import include, path
from django.contrib import flatpages
from django.conf.urls import handler404, handler500
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views


handler404 = "posts.views.page_not_found"  
handler500 = "posts.views.server_error"  

urlpatterns = [
    #  раздел администратора
    path("admin/", admin.site.urls),
    #  обработчик для главной страницы ищем в urls.py приложения posts
    path("", include("posts.urls")),

    #  регистрация и авторизация
    path("auth/", include("users.urls")),

    #  если нужного шаблона для /auth не нашлось в файле users.urls — 
    #  ищем совпадения в файле django.contrib.auth.urls
    path("auth/", include("django.contrib.auth.urls")),

    # flatpages
    path('about/', include('django.contrib.flatpages.urls')),
]

# добавим новые пути
urlpatterns += [
        path('about-us/', flatpages.views.flatpage, {'url': '/about-us/'}, name='about'),
        path('terms/', flatpages.views.flatpage, {'url': '/terms/'}, name='terms'),
        path('about-author/', flatpages.views.flatpage, {'url': '/about-author/'}, name='about-author'),
        path('about-spec/', flatpages.views.flatpage, {'url': '/about-spec/'}, name='about-spec'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += [
        path('api-token-auth/', views.obtain_auth_token)
    ]