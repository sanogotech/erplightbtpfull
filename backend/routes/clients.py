from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..models import Client, User
from ..app import db

bp = Blueprint('clients', __name__)

@bp.route('/api/clients', methods=['GET'])
@jwt_required()
def get_clients():
    clients = Client.query.all()
    return jsonify([
        {
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'address': client.address,
            'created_at': client.created_at.isoformat()
        } for client in clients
    ])

@bp.route('/api/clients/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    return jsonify({
        'id': client.id,
        'name': client.name,
        'email': client.email,
        'phone': client.phone,
        'address': client.address,
        'created_at': client.created_at.isoformat()
    })

@bp.route('/api/clients', methods=['POST'])
@jwt_required()
def create_client():
    data = request.get_json()
    
    client = Client(
        name=data['name'],
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address')
    )
    
    db.session.add(client)
    db.session.commit()
    
    return jsonify({
        'id': client.id,
        'name': client.name,
        'email': client.email,
        'phone': client.phone,
        'address': client.address,
        'created_at': client.created_at.isoformat()
    }), 201

@bp.route('/api/clients/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    client = Client.query.get_or_404(client_id)
    data = request.get_json()
    
    client.name = data.get('name', client.name)
    client.email = data.get('email', client.email)
    client.phone = data.get('phone', client.phone)
    client.address = data.get('address', client.address)
    
    db.session.commit()
    
    return jsonify({
        'id': client.id,
        'name': client.name,
        'email': client.email,
        'phone': client.phone,
        'address': client.address,
        'created_at': client.created_at.isoformat()
    })

@bp.route('/api/clients/<int:client_id>', methods=['DELETE'])
@jwt_required()
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    
    # Check if client has any projects or invoices
    if client.projects or client.invoices:
        return jsonify({'error': 'Cannot delete client with existing projects or invoices'}), 400
    
    db.session.delete(client)
    db.session.commit()
    
    return jsonify({'message': 'Client deleted successfully'})

@bp.route('/api/clients/search', methods=['GET'])
@jwt_required()
def search_clients():
    query = request.args.get('q', '')
    
    clients = Client.query.filter(
        Client.name.ilike(f'%{query}%') |
        Client.email.ilike(f'%{query}%') |
        Client.phone.ilike(f'%{query}%')
    ).all()
    
    return jsonify([
        {
            'id': client.id,
            'name': client.name,
            'email': client.email,
            'phone': client.phone,
            'address': client.address,
            'created_at': client.created_at.isoformat()
        } for client in clients
    ])