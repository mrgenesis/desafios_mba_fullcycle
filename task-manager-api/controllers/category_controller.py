from database import db
from middlewares.errors import ApiError
from models.category import Category
from models.task import Task


def list_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        data = c.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return result


def create_category(data):
    if not data:
        raise ApiError({'error': 'Dados inválidos'}, 400)

    name = data.get('name')
    if not name:
        raise ApiError({'error': 'Nome é obrigatório'}, 400)

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    db.session.add(category)
    db.session.commit()
    return category.to_dict()


def update_category(cat_id, data):
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise ApiError({'error': 'Categoria não encontrada'}, 404)

    if not data:
        raise ApiError({'error': 'Dados inválidos'}, 400)

    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    db.session.commit()
    return cat.to_dict()


def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise ApiError({'error': 'Categoria não encontrada'}, 404)

    db.session.delete(cat)
    db.session.commit()
    return {'message': 'Categoria deletada'}
