import csv
from io import StringIO, BytesIO
from app.core.aws import upload_bytes_to_s3
from app.db.session import SessionLocal
from app.models.file_model import File
from app.models.file_validation import FileValidation
from app.models.data_row import DataRow

def _validate_row(row, row_num, seen_keys):
    errors = []
    # example required field 'name'
    if not row.get('name'):
        errors.append({'row': row_num, 'column': 'name', 'error': 'EMPTY', 'message': 'name is required'})
    price = row.get('price')
    if price is not None and price != '':
        try:
            float(price)
        except:
            errors.append({'row': row_num, 'column': 'price', 'error': 'TYPE', 'message': 'price must be numeric'})
    key = row.get('id')
    if key:
        if key in seen_keys:
            errors.append({'row': row_num, 'column': 'id', 'error': 'DUPLICATE', 'message': 'duplicate id'})
        else:
            seen_keys.add(key)
    return errors

async def handle_upload(upload_file, parametro1: str, parametro2: str, uploaded_by: str = None):
    contents = await upload_file.read()
    # store original file (S3 or local)
    key = f"uploads/{upload_file.filename}"
    storage_path = upload_bytes_to_s3(contents, key)
    # process CSV
    text = contents.decode('utf-8-sig')
    reader = csv.DictReader(StringIO(text))
    validations = []
    rows_to_insert = []
    seen = set()
    row_num = 0
    for row in reader:
        row_num += 1
        errs = _validate_row(row, row_num, seen)
        if errs:
            validations.extend(errs)
        else:
            # map to DataRow
            price_val = None
            if row.get('price'):
                try:
                    price_val = float(row.get('price'))
                except:
                    price_val = None
            rows_to_insert.append({
                'external_id': row.get('id'),
                'name': row.get('name'),
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
