from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Details, Category
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
DB_NAME = os.getenv("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB_NAME}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.context_processor
def dashboard_stats():

    total = Details.query.count()
    completed = Details.query.filter_by(status=True).count()
    todo = Details.query.filter_by(status=False).count()
    categories = Category.query.count()

    return dict(
        total_tasks=total,
        completed_tasks=completed,
        todo_tasks=todo,
        category_count=categories
    )



@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST' and 'task' in request.form:
        task_data = Details(
            task=request.form['task'],
            priority=request.form['priority'],
            category=request.form['category'],
            status=False
        )
        db.session.add(task_data)
        db.session.commit()
        return redirect(url_for('home'))

    if request.method == 'POST' and 'category' in request.form:
        cat = Category(name=request.form['category'])
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for('home'))

    details = Details.query.all()
    categories = Category.query.all()

    return render_template("home.html", details=details, categories=categories)


@app.route('/status/<int:id>', methods=['POST'])
def status(id):
    task_data = Details.query.get(id)
    if task_data.status:
        task_data.status = False
    else:
        task_data.status = True
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete/<int:id>')
def delete(id):
    task_data = Details.query.get(id)
    db.session.delete(task_data)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    task_data = Details.query.get(id)

    categories = Category.query.all()

    if request.method == 'POST':
        task_data.task = request.form['task']
        task_data.priority = request.form['priority']
        task_data.category = request.form['category']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", task=task_data, categories=categories)


@app.route('/api/tasks', methods=['GET'])
def api_get_tasks():
    data = Details.query.all()
    box = []
    for d in data:
        box.append({
            "id": d.id,
            "task": d.task,
            "priority": d.priority,
            "category": d.category,
            "status": d.status
        })
    return jsonify(box)


@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json()

    task_data = Details(
        task=data['task'],
        priority=data['priority'],
        category=data['category'],
        status=False
    )

    db.session.add(task_data)
    db.session.commit()

    return jsonify({
        "message": "Task added",
        "task": task_data.task
    })


@app.route('/api/tasks/status/<int:id>', methods=['PUT'])
def api_status_task(id):
    task = Details.query.get(id)
    if task.status:
        task.status = False
    else:
        task.status = True
    db.session.commit()

    return jsonify({
        "id": task.id,
        "status": task.status
    })


@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def api_delete_task(id):
    task_data = Details.query.get(id)
    db.session.delete(task_data)
    db.session.commit()

    return jsonify({
        "status": "deleted",
        "task": task_data.task
    })


@app.route('/api/tasks/<int:id>', methods=['PUT'])
def api_edit_task(id):
    task = Details.query.get(id)

    if task.status:
        return jsonify({"error": "Completed task cannot be edited"}), 403

    data = request.get_json()

    task.task = data['task']
    task.priority = data['priority']
    task.category = data['category']
    db.session.commit()

    return jsonify({
        "message": "Task updated",
        "id": task.id
    })


@app.route('/api/categories', methods=['GET'])
def api_get_categories():
    cats = Category.query.all()
    box = []
    for c in cats:
        box.append({"id": c.id, "name": c.name})
    return jsonify(box)


@app.route('/api/categories', methods=['POST'])
def api_add_category():
    data = request.get_json()

    cat = Category(name=data['name'])
    db.session.add(cat)
    db.session.commit()

    return jsonify({
        "status": " added",
        "name": cat.name
    })

@app.route('/api/categories/<int:id>', methods=['DELETE'])
def api_delete_category(id):

    cat = Category.query.get(id)

    cat_data = Details.query.filter_by(category=cat.name)
    cat_data.delete()  
    db.session.delete(cat)
    db.session.commit()

    return jsonify({
        "message": "Category deleted",
        "id": id
    })

@app.route('/delete_category/<int:id>')
def delete_category(id):

    cat = Category.query.get(id)
    cat_data = Details.query.filter_by(category=cat.name)
    cat_data.delete()
    db.session.delete(cat)
    db.session.commit()

    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run(debug=True)
