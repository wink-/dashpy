from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required
from sqlalchemy import or_
from models.calsys import (
    Device, Calibration, Employee, Location, Owner,
    Period, Source, Status, Type, CalibratedBy,
    get_calibration_due, get_cal_export
)
from models import db
from datetime import datetime
import csv
import io
import pandas as pd

bp = Blueprint('calsys', __name__, url_prefix='/api/calsys')

def paginate_query(query, schema=None):
    """Helper function to paginate query results"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = min(per_page, 100)  # Limit maximum items per page
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return {
        'items': [item.to_dict() for item in paginated.items],
        'total': paginated.total,
        'page': page,
        'per_page': per_page,
        'pages': paginated.pages
    }

@bp.route('/devices', methods=['GET'])
@login_required
def get_devices():
    """Get all devices with filtering, search, and pagination"""
    query = Device.query
    
    # Search functionality
    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            Device.name.ilike(search_term),
            Device.description.ilike(search_term),
            Device.serialNumber.ilike(search_term)
        ))
    
    # Advanced filtering
    location = request.args.get('location')
    if location:
        query = query.filter(Device.location == location)
    
    device_type = request.args.get('type')
    if device_type:
        query = query.filter(Device.typeID == device_type)
    
    owner = request.args.get('owner')
    if owner:
        query = query.filter(Device.ownerID == owner)
    
    period = request.args.get('period')
    if period:
        query = query.filter(Device.period == period)
    
    # Sort options
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    if hasattr(Device, sort_by):
        sort_column = getattr(Device, sort_by)
        if sort_order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
    
    # Handle export request
    if request.args.get('export'):
        format = request.args.get('format', 'csv')
        return export_query(query, format, 'devices')
    
    # Paginate results
    result = paginate_query(query)
    
    # Enhance response with related data
    enhanced_items = [{
        **item,
        'type_name': Device.query.get(item['ID']).device_type.name if Device.query.get(item['ID']).device_type else None,
        'location_name': Device.query.get(item['ID']).device_location.name if Device.query.get(item['ID']).device_location else None,
        'owner_name': Device.query.get(item['ID']).owner.name if Device.query.get(item['ID']).owner else None,
        'source_name': Device.query.get(item['ID']).source.name if Device.query.get(item['ID']).source else None
    } for item in result['items']]
    
    result['items'] = enhanced_items
    return jsonify(result)

@bp.route('/calibrations', methods=['GET'])
@login_required
def get_calibrations():
    """Get calibrations with filtering, search, and pagination"""
    query = Calibration.query
    
    # Search functionality
    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.join(Device).filter(or_(
            Device.name.ilike(search_term),
            Device.serialNumber.ilike(search_term)
        ))
    
    # Advanced filtering
    device_id = request.args.get('device_id')
    if device_id:
        query = query.filter(Calibration.deviceID == device_id)
    
    status = request.args.get('status')
    if status:
        query = query.filter(Calibration.status == status)
    
    start_date = request.args.get('start_date')
    if start_date:
        query = query.filter(Calibration.calDate >= start_date)
    
    end_date = request.args.get('end_date')
    if end_date:
        query = query.filter(Calibration.calDate <= end_date)
    
    employee_id = request.args.get('employee_id')
    if employee_id:
        query = query.filter(Calibration.employeeID == employee_id)
    
    # Sort options
    sort_by = request.args.get('sort_by', 'calDate')
    sort_order = request.args.get('sort_order', 'desc')
    
    if hasattr(Calibration, sort_by):
        sort_column = getattr(Calibration, sort_by)
        if sort_order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
    
    # Handle export request
    if request.args.get('export'):
        format = request.args.get('format', 'csv')
        return export_query(query, format, 'calibrations')
    
    # Paginate results
    result = paginate_query(query)
    
    # Enhance response with related data
    enhanced_items = [{
        **item,
        'device_name': Calibration.query.get(item['ID']).device.name if Calibration.query.get(item['ID']).device else None,
        'calibrated_by_name': Calibration.query.get(item['ID']).calibrated_by.name if Calibration.query.get(item['ID']).calibrated_by else None,
        'employee_name': Calibration.query.get(item['ID']).employee.name if Calibration.query.get(item['ID']).employee else None,
        'status_name': Calibration.query.get(item['ID']).status_info.name if Calibration.query.get(item['ID']).status_info else None
    } for item in result['items']]
    
    result['items'] = enhanced_items
    return jsonify(result)

def export_query(query, format='csv', filename_prefix='export'):
    """Export query results to CSV or Excel"""
    # Convert query results to pandas DataFrame
    data = [item.to_dict() for item in query.all()]
    df = pd.DataFrame(data)
    
    # Create in-memory buffer
    output = io.BytesIO()
    
    if format == 'excel':
        # Export to Excel
        df.to_excel(output, index=False, engine='openpyxl')
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'
    else:
        # Export to CSV
        df.to_csv(output, index=False)
        mimetype = 'text/csv'
        extension = 'csv'
    
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(
        output,
        mimetype=mimetype,
        as_attachment=True,
        download_name=f'{filename_prefix}_{timestamp}.{extension}'
    )

# Lookup endpoints with pagination and search
@bp.route('/lookup/<string:table>', methods=['GET'])
@login_required
def lookup(table):
    """Generic lookup endpoint for all reference tables"""
    table_map = {
        'locations': Location,
        'types': Type,
        'owners': Owner,
        'sources': Source,
        'periods': Period,
        'statuses': Status,
        'employees': Employee,
        'calibrated-by': CalibratedBy
    }
    
    if table not in table_map:
        return jsonify({'error': 'Invalid lookup table'}), 404
    
    model = table_map[table]
    query = model.query
    
    # Search functionality
    search = request.args.get('search')
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            model.name.ilike(search_term),
            model.ID.ilike(search_term)
        ))
    
    # Sort options
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    if hasattr(model, sort_by):
        sort_column = getattr(model, sort_by)
        if sort_order == 'desc':
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
    
    return jsonify(paginate_query(query))

@bp.route('/calibration-due', methods=['GET'])
@login_required
def calibration_due():
    """Get list of devices due for calibration with filtering and export"""
    result = get_calibration_due(db.session)
    data = [dict(row) for row in result]
    
    if request.args.get('export'):
        df = pd.DataFrame(data)
        format = request.args.get('format', 'csv')
        output = io.BytesIO()
        
        if format == 'excel':
            df.to_excel(output, index=False, engine='openpyxl')
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            extension = 'xlsx'
        else:
            df.to_csv(output, index=False)
            mimetype = 'text/csv'
            extension = 'csv'
        
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f'calibration_due_{timestamp}.{extension}'
        )
    
    return jsonify(data)

@bp.route('/cal-export', methods=['GET'])
@login_required
def cal_export():
    """Get calibration export data with export options"""
    result = get_cal_export(db.session)
    data = [dict(row) for row in result]
    
    if request.args.get('export'):
        df = pd.DataFrame(data)
        format = request.args.get('format', 'csv')
        output = io.BytesIO()
        
        if format == 'excel':
            df.to_excel(output, index=False, engine='openpyxl')
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            extension = 'xlsx'
        else:
            df.to_csv(output, index=False)
            mimetype = 'text/csv'
            extension = 'csv'
        
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f'cal_export_{timestamp}.{extension}'
        )
    
    return jsonify(data)
