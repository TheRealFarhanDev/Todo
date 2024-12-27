from flask import Flask, render_template, request, redirect, flash
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.todo}"
    
class Done(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    done = db.Column(db.String(100), nullable=True)
    
    def __repr__(self) -> str:
        return f"{self.done}"

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":
        task = request.form.get('todo')
        if task:
            todo = Todo(todo=task)
            db.session.add(todo)
            db.session.commit()
        else:
            return flash("Field Required!,it cannot be empty")
        return redirect("/")

    allTodo = Todo.query.all()
    allDone = Done.query.all()
    total_sno = db.session.query(func.count(Todo.sno)).scalar() or 0
    total_sno_done = db.session.query(func.count(Done.done)).scalar() or 0
    return render_template('index.html' , allTodo=allTodo, allDone=allDone, totalSno=total_sno, totalSnoDone=total_sno_done)

@app.route('/delete/<int:sno>', methods=['POST'])
def delete(sno):
    todo_to_delete = Todo.query.filter_by(sno=sno).first()
    if todo_to_delete:
        db.session.delete(todo_to_delete)
        db.session.commit()
    return redirect("/")

@app.route('/delete-done/<int:sno>', methods=['POST'])
def deletedone(sno):
    todo_to_delete = Done.query.filter_by(sno=sno).first()
    if todo_to_delete:
        db.session.delete(todo_to_delete)
        db.session.commit()
    return redirect("/")


@app.route('/done/<int:sno>', methods=['POST'])
def done(sno):
    # Retrieve the task from the Todo table
    todo_to_done = Todo.query.filter_by(sno=sno).first()

    # Check if the task exists
    if not todo_to_done:
        flash("Todo item not found!")
        return redirect('/')

    # Add the task to the Done table
    done_task = Done(done=todo_to_done.todo)
    db.session.add(done_task)

    # Delete the task from the Todo table
    db.session.delete(todo_to_done)
    db.session.commit()

    flash("Task marked as done!")
    return redirect("/")
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=8000, debug=True)
 