from django.urls import include, path
from . import views

urlpatterns = [
    path("tables/", views.XmlTableList.as_view(), name="xmltable-list"),
    path(
        "table/<str:tablename>/", views.XmlTableDetail.as_view(), name="xmltable-detail"
    ),
]
