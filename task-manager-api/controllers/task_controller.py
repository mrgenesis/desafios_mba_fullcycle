from datetime import datetime

from sqlalchemy.orm import joinedload

from database import db
from middlewares.errors import ApiError
from models.category import Category
from models.task import Task
from models.user import User

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']


def _serialize_with_names(t):
    data = t.to_dict()
    data['overdue'] = t.is_overdue()
    data['user_name'] = t.user.name if t.user else None
    data['category_name'] = t.category.name if t.category else None
    return data


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    return [_serialize_with_names(t) for t in tasks]


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise ApiError({'error': 'Task não encontrada'}, 404)

    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def create_task(data):
    if not data:
        raise ApiError({'error': 'Dados inválidos'}, 400)

    title = data.get('title')
    if not title:
        raise ApiError({'error': 'Título é obrigatório'}, 400)
    if len(title) < 3:
        raise ApiError({'error': 'Título muito curto'}, 400)
    if len(title) > 200:
        raise ApiError({'error': 'Título muito longo'}, 400)

    description = data.get('description', '')
    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date = data.get('due_date')
    tags = data.get('tags')

    if status not in VALID_STATUSES:
        raise ApiError({'error': 'Status inválido'}, 400)

    if priority < 1 or priority > 5:
        raise ApiError({'error': 'Prioridade deve ser entre 1 e 5'}, 400)

    if user_id:
        user = db.session.get(User, user_id)
        if not user:
            raise ApiError({'error': 'Usuário não encontrado'}, 404)

    if category_id:
        cat = db.session.get(Category, category_id)
        if not cat:
            raise ApiError({'error': 'Categoria não encontrada'}, 404)

    task = Task()
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            raise ApiError({'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400)

    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    return task.to_dict()


def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        raise ApiError({'error': 'Task não encontrada'}, 404)

    if not data:
        raise ApiError({'error': 'Dados inválidos'}, 400)

    if 'title' in data:
        if len(data['title']) < 3:
            raise ApiError({'error': 'Título muito curto'}, 400)
        if len(data['title']) > 200:
            raise ApiError({'error': 'Título muito longo'}, 400)
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            raise ApiError({'error': 'Status inválido'}, 400)
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < 1 or data['priority'] > 5:
            raise ApiError({'error': 'Prioridade deve ser entre 1 e 5'}, 400)
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id']:
            user = db.session.get(User, data['user_id'])
            if not user:
                raise ApiError({'error': 'Usuário não encontrado'}, 404)
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id']:
            cat = db.session.get(Category, data['category_id'])
            if not cat:
                raise ApiError({'error': 'Categoria não encontrada'}, 404)
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                raise ApiError({'error': 'Formato de data inválido'}, 400)
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    task.updated_at = datetime.utcnow()

    db.session.commit()
    return task.to_dict()


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise ApiError({'error': 'Task não encontrada'}, 404)

    db.session.delete(task)
    db.session.commit()
    return {'message': 'Task deletada com sucesso'}


def search_tasks(query, status, priority_raw, user_id_raw):
    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
        )

    if status:
        tasks = tasks.filter(Task.status == status)

    if priority_raw:
        try:
            priority = int(priority_raw)
        except ValueError:
            raise ApiError({'error': 'priority inválido'}, 400)
        tasks = tasks.filter(Task.priority == priority)

    if user_id_raw:
        try:
            user_id = int(user_id_raw)
        except ValueError:
            raise ApiError({'error': 'user_id inválido'}, 400)
        tasks = tasks.filter(Task.user_id == user_id)

    return [t.to_dict() for t in tasks.all()]


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())

    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
