from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models import Invoice, Payment, ERPExport, User
from ..app import db
import json
import os

bp = Blueprint('exports', __name__)

@bp.route('/api/exports/pending', methods=['GET'])
@jwt_required()
def get_pending_exports():
    # Get pending invoices and payments for export
    pending_invoices = Invoice.query.filter_by(export_status='pending').all()
    pending_payments = Payment.query.filter_by(export_status='pending').all()
    
    return jsonify({
        'invoices': [
            {
                'id': inv.id,
                'reference': inv.reference,
                'total_amount': inv.total_amount,
                'client_name': inv.client.name,
                'created_at': inv.created_at.isoformat()
            } for inv in pending_invoices
        ],
        'payments': [
            {
                'id': pay.id,
                'amount': pay.amount,
                'payment_date': pay.payment_date.isoformat(),
                'reference': pay.reference,
                'invoice_reference': pay.invoice.reference
            } for pay in pending_payments
        ]
    })

@bp.route('/api/exports/generate', methods=['POST'])
@jwt_required()
def generate_export():
    data = request.get_json()
    export_type = data.get('type')  # 'invoice' or 'payment'
    record_ids = data.get('record_ids', [])
    
    if not export_type or not record_ids:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        # Create export records
        exports = []
        if export_type == 'invoice':
            records = Invoice.query.filter(Invoice.id.in_(record_ids)).all()
            export_data = [
                {
                    'invoice_reference': r.reference,
                    'date': r.created_at.isoformat(),
                    'client': {
                        'name': r.client.name,
                        'address': r.client.address
                    },
                    'amount': r.total_amount,
                    'status': r.status
                } for r in records
            ]
        else:  # payment
            records = Payment.query.filter(Payment.id.in_(record_ids)).all()
            export_data = [
                {
                    'payment_reference': r.reference,
                    'date': r.payment_date.isoformat(),
                    'amount': r.amount,
                    'method': r.payment_method,
                    'invoice_reference': r.invoice.reference
                } for r in records
            ]
        
        # Generate export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'jde_export_{export_type}_{timestamp}.json'
        export_path = os.path.join('exports', filename)
        
        os.makedirs('exports', exist_ok=True)
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # Update export status
        for record in records:
            record.export_status = 'exported'
            export = ERPExport(
                type=export_type,
                status='success',
                record_id=record.id,
                export_date=datetime.utcnow()
            )
            exports.append(export)
        
        db.session.add_all(exports)
        db.session.commit()
        
        return jsonify({
            'message': 'Export generated successfully',
            'filename': filename,
            'record_count': len(records)
        })
        
    except Exception as e:
        # Log error and update status
        for record_id in record_ids:
            export = ERPExport(
                type=export_type,
                status='failed',
                record_id=record_id,
                error_message=str(e),
                export_date=datetime.utcnow()
            )
            db.session.add(export)
        
        db.session.commit()
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@bp.route('/api/exports/history', methods=['GET'])
@jwt_required()
def get_export_history():
    exports = ERPExport.query.order_by(ERPExport.created_at.desc()).limit(100).all()
    return jsonify([
        {
            'id': export.id,
            'type': export.type,
            'status': export.status,
            'record_id': export.record_id,
            'export_date': export.export_date.isoformat() if export.export_date else None,
            'error_message': export.error_message,
            'created_at': export.created_at.isoformat()
        } for export in exports
    ])