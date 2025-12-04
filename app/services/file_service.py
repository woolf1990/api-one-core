import csv
from io import StringIO, BytesIO
import pandas as pd
from app.core.aws import upload_bytes_to_s3
from app.db.session import SessionLocal
from app.models.file_model import File
from app.models.file_validation import FileValidation
from app.models.data_row import DataRow

def _is_empty_value(value):
    """Verifica si un valor está vacío (None, NaN, string vacío)."""
    if value is None:
        return True
    if isinstance(value, float):
        # Verificar NaN
        try:
            import math
            return math.isnan(value)
        except:
            return False
    if isinstance(value, str):
        return value.strip() == ''
    return False

def _validate_row_basic(row, row_num):
    """
    Valida una fila del archivo (validaciones básicas sin duplicados).
    - name: requerido
    - price: requerido y debe ser numérico
    Retorna: (errors, name_normalized) donde name_normalized es el nombre normalizado si es válido, None si no
    """
    errors = []
    name_normalized = None
    
    # Validar campo 'name' (requerido)
    name_value = row.get('name')
    if _is_empty_value(name_value):
        errors.append({'row': row_num, 'column': 'name', 'error': 'EMPTY', 'message': 'name is required and cannot be empty'})
    else:
        # Normalizar nombre
        name_str = str(name_value).strip()
        if name_str:
            name_normalized = name_str
        else:
            errors.append({'row': row_num, 'column': 'name', 'error': 'EMPTY', 'message': 'name is required and cannot be empty'})
    
    # Validar campo 'price' (requerido y debe ser numérico)
    price = row.get('price')
    if _is_empty_value(price):
        errors.append({'row': row_num, 'column': 'price', 'error': 'EMPTY', 'message': 'price is required and cannot be empty'})
    else:
        # Validar que sea numérico
        try:
            float(price)
        except (ValueError, TypeError):
            errors.append({'row': row_num, 'column': 'price', 'error': 'TYPE', 'message': 'price must be numeric'})
    
    return errors, name_normalized

async def handle_upload(upload_file, parametro1: str, parametro2: str, uploaded_by: str = None):
    contents = await upload_file.read()
    # store original file (S3 or local)
    key = f"uploads/{upload_file.filename}"
    storage_path = upload_bytes_to_s3(contents, key)
    
    # Detectar tipo de archivo y procesar
    filename_lower = (upload_file.filename or "").lower()
    is_excel = filename_lower.endswith((".xlsx", ".xls"))
    
    # Leer datos según el tipo de archivo
    if is_excel:
        # Procesar Excel con pandas
        df = pd.read_excel(BytesIO(contents), engine='openpyxl')
        # Normalizar nombres de columnas: eliminar espacios y convertir a minúsculas
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        # Convertir DataFrame a lista de diccionarios (similar a CSV DictReader)
        # Convertir NaN a None para compatibilidad
        rows = df.replace({pd.NA: None, pd.NaT: None}).to_dict('records')
    else:
        # Procesar CSV
        text = contents.decode('utf-8-sig')
        reader = csv.DictReader(StringIO(text))
        # Normalizar nombres de columnas del CSV también
        rows = []
        for row in reader:
            normalized_row = {k.strip().lower().replace(' ', '_'): v for k, v in row.items()}
            rows.append(normalized_row)
    
    # Primera pasada: validar todas las filas (sin duplicados)
    validations = []
    valid_rows_data = []  # Almacena (row_num, row, name_normalized) de filas que pasan validación básica
    
    row_num = 0
    for row in rows:
        row_num += 1
        # Validar la fila (validaciones básicas)
        errs, name_normalized = _validate_row_basic(row, row_num)
        
        # Agregar todos los errores encontrados
        if errs:
            validations.extend(errs)
        else:
            # Si pasa validación básica, guardar para segunda pasada (validar duplicados)
            valid_rows_data.append((row_num, row, name_normalized))
    
    # Segunda pasada: validar duplicados solo entre filas válidas
    seen_names = set()
    rows_to_insert = []
    
    for row_num, row, name_normalized in valid_rows_data:
        # Verificar duplicados
        if name_normalized in seen_names:
            validations.append({'row': row_num, 'column': 'name', 'error': 'DUPLICATE', 'message': f'duplicate name: {name_normalized}'})
        else:
            seen_names.add(name_normalized)
            
            # Preparar la fila para insertar (ya validada completamente)
            # Convertir price a float
            price_raw = row.get('price')
            price_val = float(price_raw)  # Ya validado que es numérico
            
            # Obtener external_id (opcional, puede ser None)
            external_id = row.get('id')
            if _is_empty_value(external_id):
                external_id = None
            else:
                external_id = str(external_id).strip() if external_id else None
            
            # Agregar a la lista de filas válidas para insertar
            rows_to_insert.append({
                'external_id': external_id,
                'name': name_normalized,
                'price': price_val,
                'uploaded_by': uploaded_by
            })
    # save metadata and rows
    db = SessionLocal()
    try:
        file_rec = File(filename=upload_file.filename, storage_path=storage_path, uploaded_by=uploaded_by)
        db.add(file_rec)
        db.commit()
        db.refresh(file_rec)
        # insert rows
        for r in rows_to_insert:
            dr = DataRow(**r)
            db.add(dr)
        db.commit()
        # save validations
        for v in validations:
            fv = FileValidation(file_id=file_rec.id, row_number=v['row'], column_name=v['column'], error_code=v['error'], message=v.get('message'))
            db.add(fv)
        db.commit()
        return {
            'file_id': file_rec.id,
            's3_path': storage_path,
            'rows_saved': len(rows_to_insert),
            'validations': validations
        }
    finally:
        db.close()
