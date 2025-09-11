import pandas as pd
from typing import List, Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
# Se añade la importación que faltaba
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows
from app.domain.reporting.report_generator import IReportGenerator
from app.domain.entities.entities import Ticket

class ExcelReportGenerator(IReportGenerator):
    def generar(self, datos: List[Any], ruta_archivo: str, header_data: Dict) -> str:
        tickets: List[Ticket] = datos
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte de Tickets"

        # --- ESTILOS ---
        header_font = Font(name='Calibri', size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", fill_type="solid")
        title_font = Font(name='Calibri', size=12, bold=True, color="4F81BD")
        cell_font = Font(name='Calibri', size=11)
        data_fill = PatternFill(start_color="FFFFCC", fill_type="solid")
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        
        # --- CABECERA DEL REPORTE ---
        ws['B2'] = "REPORTE DE TICKETS SEMANAL"
        ws['B2'].font = title_font
        
        ws['B4'] = "SEMANA DEL INFORME"
        ws['B4'].font = title_font
        ws['B5'] = header_data['fecha_inicio'].strftime('%d de %B de %Y')
        
        ws['B7'] = "GENERADO POR"
        ws['B7'].font = title_font
        ws['B8'] = header_data['generado_por']
        
        ws['E4'] = "COMENTARIOS"
        ws['E4'].font = title_font
        ws.merge_cells('E5:I9')
        ws['E5'] = header_data['comentarios']
        ws['E5'].alignment = Alignment(wrap_text=True, vertical='top', horizontal='left')
        
        # --- TABLA DE DATOS ---
        start_row = 12
        if not tickets:
            ws.cell(row=start_row, column=2, value="No se encontraron tickets para esta semana.")
            wb.save(ruta_archivo)
            return ruta_archivo

        data_for_df = [t.__dict__ for t in tickets]
        df = pd.DataFrame(data_for_df)
        
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%Y-%m-%d %H:%M')
        column_map = {
            "fecha": "FECHA",
            "numero_ticket": "NUM TICKET",
            "servicio": "SERVICIO",
            "usuario_reporta": "USUARIO",
            "correo_usuario": "CORREO",
            "empresa": "EMPRESA"
        }
        report_df = df[list(column_map.keys())].rename(columns=column_map)

        header_row = list(report_df.columns)
        for col_idx, header_title in enumerate(header_row, 2):
            cell = ws.cell(row=start_row, column=col_idx, value=header_title)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        for row_idx, row_data in enumerate(report_df.itertuples(index=False), start_row + 1):
            for col_idx, cell_value in enumerate(row_data, 2):
                cell = ws.cell(row=row_idx, column=col_idx, value=cell_value)
                cell.font = cell_font
                cell.fill = data_fill
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='left')
        
        for col_idx, column_title in enumerate(header_row, 2):
            column_letter = get_column_letter(col_idx)
            max_length = len(column_title)
            for i in range(len(report_df)):
                cell_content = str(report_df.iloc[i, col_idx - 2])
                if len(cell_content) > max_length:
                    max_length = len(cell_content)
            adjusted_width = max_length + 4
            ws.column_dimensions[column_letter].width = adjusted_width

        wb.save(ruta_archivo)
        return ruta_archivo