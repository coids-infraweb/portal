import random
import string
import datetime
from builtins import range
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.encoding import force_str, force_text
from django.utils.http import urlsafe_base64_decode
from apps.colaborador.models import Colaborador
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill


def gerar_password():
    password = ""
    for ay in list(range(3)):
        i = random.choice(string.ascii_lowercase)
        password += i
    password += random.choice(string.punctuation )
    for ay in list(range(2)):
        o = random.choice(string.digits)
        password += o
    password += random.choice(string.punctuation )
    for ay in list(range(3)):
        u = random.choice(string.ascii_uppercase)
        password += u
    return password


def get_user(uidb64):
    try:
        pk = urlsafe_base64_decode(uidb64).decode()
        user = Colaborador._default_manager.get(pk=pk)
    except (TypeError, ValueError, OverflowError, Colaborador.DoesNotExist, ValidationError):
        user = None
    return user


class HistoryColaborador:
    def __init__(self, request=None):
        self.request = request

    def responsavel(self, colaborador_grupoacesso, status):
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador_grupoacesso.colaborador).pk, object_id=colaborador_grupoacesso.colaborador.pk,
            object_repr=force_str(colaborador_grupoacesso.colaborador), action_flag=ADDITION,
            change_message=(f"Solicitação de acesso aos recursos do Grupo de Trabalho {colaborador_grupoacesso.grupo_acesso.grupo_acesso} - {status}")
        )
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador_grupoacesso.grupo_acesso).pk,
            object_id=colaborador_grupoacesso.grupo_acesso.pk,
            object_repr=force_str(colaborador_grupoacesso.grupo_acesso), action_flag=ADDITION,
            change_message=(f"Solicitação do Colaborador {colaborador_grupoacesso.colaborador.full_name} - {status}"),
        )
    
    def responsavel_remover_grupo_acesso(self, colaborador_grupoacesso):
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador_grupoacesso.colaborador).pk, object_id=colaborador_grupoacesso.colaborador.pk,
            object_repr=force_str(colaborador_grupoacesso.colaborador), action_flag=ADDITION,
            change_message=(f"O acesso aos recursos do Grupo de Trabalho {colaborador_grupoacesso.grupo_acesso.grupo_acesso} foram removidos")
        )
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador_grupoacesso.grupo_acesso).pk,
            object_id=colaborador_grupoacesso.grupo_acesso.pk,
            object_repr=force_str(colaborador_grupoacesso.grupo_acesso), action_flag=ADDITION,
            change_message=(f"O acesso do Colaborador {colaborador_grupoacesso.colaborador} foi removido")
        )
    
    def responsavel_remover_grupo(self, colaborador_grupoacesso):
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador_grupoacesso.colaborador).pk, object_id=colaborador_grupoacesso.colaborador.pk,
            object_repr=force_str(colaborador_grupoacesso.colaborador), action_flag=ADDITION,
            change_message=(f"O acesso ao Grupo de Trabalho {colaborador_grupoacesso.grupo_acesso.grupo_acesso} foi removido")
        )
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador_grupoacesso.grupo_acesso.grupo_trabalho).pk,
            object_id=colaborador_grupoacesso.grupo_acesso.grupo_trabalho.pk,
            object_repr=force_str(colaborador_grupoacesso.grupo_acesso.grupo_trabalho), action_flag=ADDITION,
            change_message=(f"O acesso do Colaborador {colaborador_grupoacesso.colaborador} foi removido")
        )

    def novo(self, colaborador):
        LogEntry.objects.log_action( user_id=colaborador.pk, 
        content_type_id=ContentType.objects.get_for_model(colaborador).pk, 
        object_id=colaborador.pk, 
        object_repr=force_str(colaborador), action_flag=ADDITION, 
        change_message=("Solicitação de Cadastro")
        )

    def suporte(self, colaborador):
        LogEntry.objects.log_action(
            user_id=self.request.user.pk, content_type_id=ContentType.objects.get_for_model(colaborador).pk, object_id=colaborador.pk, object_repr=force_str(colaborador), action_flag=ADDITION, change_message=("Conta criada pelo suporte")
        )

    def secretaria(self, colaborador):
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador).pk,
            object_id=colaborador.pk,
            object_repr=force_str(colaborador), action_flag=ADDITION,
            change_message=(f"Cadastro revisado pela Secretaria da {colaborador.divisao.divisao}"),
        )

    def chefia(self, colaborador):
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador).pk,
            object_id=colaborador.pk,
            object_repr=force_str(colaborador), action_flag=ADDITION,
            change_message=(f"Cadastro aprovado pela chefia da {colaborador.divisao.divisao}"),
        )

    def solicitacao(self, colaborador, grupo_acesso):
        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(colaborador).pk,
            object_id=colaborador.pk,
            object_repr=force_str(colaborador),
            action_flag=ADDITION,
            change_message=(f"Solicitação de acesso aos recursos do Grupo de Trabalho {grupo_acesso.grupo_acesso}"),
        )

        LogEntry.objects.log_action( user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(grupo_acesso).pk,
            object_id=grupo_acesso.pk,
            object_repr=force_str(grupo_acesso),
            action_flag=ADDITION,
            change_message=(f"Solicitado acesso aos recursos do Grupo de Trabalho por {colaborador.full_name} "),
        )


def export_to_xlsx(queryset, fields, title="Relatório", filename="relatorio.xlsx"):
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Dados"

        ws.merge_cells('A1:{}1'.format(chr(65 + len(fields) - 1)))
        title_cell = ws["A1"]
        title_cell.value = title
        title_cell.font = Font(size=14, bold=True, color="FFFFFF")
        title_cell.alignment = Alignment(horizontal="center")
        title_cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")

        header_row = []
        for field in fields:
            header_row.append(field)
        
        ws.append(header_row)

        for col_num, column_title in enumerate(header_row, 1):
            cell = ws.cell(row=2, column=col_num, value=column_title)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")

        for obj in queryset:
            row = [getattr(obj, field, "") for field in fields]
            ws.append(row)

        for col in ws.iter_cols(min_row=2, max_row=ws.max_row):
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if not isinstance(cell, type(ws.cell(row=1, column=1))):
                    continue
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            ws.column_dimensions[col_letter].width = max_length + 2

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        wb.save(response)
        return response

    except Exception as err:
        print(f'Erro ao gerar o Excel: {err}')
        return HttpResponse("Erro ao gerar o arquivo.", status=500)


def export_to_pdf(queryset=None, fields=None, filename=None):
    try:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        
        doc = SimpleDocTemplate(response, pagesize=letter)
        
        # ESSE CAMPO AQUI É OQ VAI CRIAR OS TITULOS DA TABELA, ENTÃO PODEMOS COLOCAR ELE NO FORMATO DENTRO DE LISTAS E DESSA MANEIRA
        # ['NOME', 'ENDEREÇO', 'EMAIL', 'RAMAL', 'VINCULO'] ---> EXEMPLO
        data = [fields]
        
        for colaborador in queryset:
            row = [getattr(colaborador, field) for field in fields]
            data.append(row)
        
        table = Table(data)
        
        style = TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('SIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, (0, 0, 0)),
            ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
        ])
        table.setStyle(style)
        doc.build([table])
        return response
    except Exception as err:
        print(f'CARA DE ERRO AQUI VEY: {err}')
        return None
