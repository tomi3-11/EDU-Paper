from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Exam, Question

exams = Blueprint('exams', __name__)

# List all exams
@exams.route('/exam')
@login_required
def list_exams():
    my_exams = Exam.query.filter_by(owner_id=current_user.id).all()
    return render_template('exams/listhtml', exams=my_exams)


# Create new exam
@exams.route('/exams/create', methods=['GET', 'POST'])
@login_required
def create_exam():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title.strip():
            flash("Title is required", "danger")
            return redirect(url_for('exams.create_exam'))
        
        new_exam = Exam(title=title, description=description, owner_id=current_user.id)
        db.session.add(new_exam)
        db.commit()
        
        flash("Exam created successfully", "success")
        return redirect(url_for('exams.list_exams'))
    
    return render_template('exams/create.html')


# Edit exam details
@exams.route('/exams/<int:exam_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    
    if exam.owner_id != current_user.id:
        flash("not Allowed", "danger")
        return redirect(url_for('exam.list_exams'))
    
    if request.method == 'POST':
        exam.title = request.form.get('title', exam.title)
        exam.description = request.form.get('description', exam.description)
        db.session.commit()
        
        flash("Exam updated", "success")
        return redirect(url_for('exams.list_exams'))
    
    return render_template('exams/edit.html', exam=exam)