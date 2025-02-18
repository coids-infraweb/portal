from django.urls import path
from apps.colaborador.views import InicioView, NovoView, SucessoView, export_colaboradores_to_pdf, export_colaboradores_to_excel
from django.contrib.auth import views as auth_views

app_name = "colaborador_open"

urlpatterns = [
    path("inicio/", InicioView.as_view(), name="inicio"),
    path("inicio/novo/", NovoView.as_view(), name="novo"),
    path("sucesso/", SucessoView.as_view(), name="sucesso"),
    path('export_excel/', export_colaboradores_to_excel, name='colaborador_colaborador_export_excel'),
    path('export_pdf/', export_colaboradores_to_pdf, name='colaborador_colaborador_export_pdf'),
]
