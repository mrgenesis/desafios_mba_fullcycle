import re

from database import db
from middlewares.errors import ApiError
from models.task import Task
from models.user import User

EMAIL_RE = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'
VALID_ROLES = ['user', 'admin', 'manager']


def list_users():
    users = User.query.all()
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'active': u.active,
            'created_at': str(u.created_at),
            'task_count': len(u.tasks),
        })
    return result


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError({'error': 'Usuário não encontrado'}, 404)

    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data['tasks'] = [t.to_dict() for t in tasks]
    return data


def create_user(data):
    if not data:
        raise ApiError({'error': 'Dados inválidos'}, 400)

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise ApiError({'error': 'Nome é obrigatório'}, 400)
    if not email:
        raise ApiError({'error': 'Email é obrigatório'}, 400)
    if not password:
        raise ApiError({'error': 'Senha é obrigatória'}, 400)

    if not re.match(EMAIL_RE, email):
        raise ApiError({'error': 'Email inválido'}, 400)

    if len(password) < 4:
        raise ApiError({'error': 'Senha deve ter no mínimo 4 caracteres'}, 400)

    existing = User.query.filter_by(email=email).first()
    if existing:
        raise ApiError({'error': 'Email já cadastrado'}, 409)

    if role not in VALID_ROLES:
        raise ApiError({'error': 'Role inválido'}, 400)

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    db.session.add(user)
    db.session.commit()

    return user.to_dict()


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError({'error': 'Usuário não encontrado'}, 404)

    if not data:
        raise ApiError({'error': 'Dados inválidos'}, 400)

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not re.match(EMAIL_RE, data['email']):
            raise ApiError({'error': 'Email inválido'}, 400)

        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ApiError({'error': 'Email já cadastrado'}, 409)
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < 4:
            raise ApiError({'error': 'Senha muito curta'}, 400)
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            raise ApiError({'error': 'Role inválido'}, 400)
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError({'error': 'Usuário não encontrado'}, 404)

    tasks = Task.query.filter_by(user_id=user_id).all()
    for t in tasks:
        db.session.delete(t)

    db.session.delete(user)
    db.session.commit()
    return {'message': 'Usuário deletado com sucesso'}


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError({'error': 'Usuário não encontrado'}, 404)

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        result.append({
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'created_at': str(t.created_at),
            'due_date': str(t.due_date) if t.due_date else None,
            'overdue': t.is_overdue(),
        })
    return result


def login(data):
    if not data:
        raise ApiError({'error': 'Dados inválidos'}, 400)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        raise ApiError({'error': 'Email e senha são obrigatórios'}, 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        raise ApiError({'error': 'Credenciais inválidas'}, 401)

    if not user.check_password(password):
        raise ApiError({'error': 'Credenciais inválidas'}, 401)

    if not user.active:
        raise ApiError({'error': 'Usuário inativo'}, 403)

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': 'fake-jwt-token-' + str(user.id),
    }
