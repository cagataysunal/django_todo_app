from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("todos/", include("todos.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", RedirectView.as_view(url="/todos/", permanent=True)),
]
