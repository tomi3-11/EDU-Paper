from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ...extensions import db
from ...models import Question, AnswerOption

bp = Blueprint('questions', __name__, template_folder='templates', url_prefix='/questions')

@bp.route('/')
@login_required
def list_questions():
    qs = Question.query.filter_by(owner_id=current_user.id).order_by(Question.created_at.desc()).all()
    return render_template('questions/list.html', questions=qs)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_question():
    if request.method == 'POST':
        qtype = request.form.get('type')
        text = request.form.get('text', '').strip()
        marks = int(request.form.get('marks') or 1)
        
        if not text:
            flash("Question text cannot be empty.", "warning")
            return redirect(url_for('questions.new_question'))
        
        q = Question(type=qtype, text=text, marks=marks, owner_id=current_user.id, school_id=current_user.school_id)
        db.session.add(q)
        db.session.commit()
        
        # MCQs: collect options + correct label
        if qtype == 'MCQs':
            options = request.form.getlist('option_text')
            correct = request.form.get('correct_label')
            labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            for i, t in enumerate(options):
                if not t or not t.strip():
                    continue
                ao = AnswerOption(question_id=q.id, text=t.strip(), label=labels[i], is_correct=(labels[i] == correct))
                db.session.add(ao)
                
            db.session.commit()
            
        # True/False or Tick or Cross: create two options automatically
        elif qtype in ('TF', 'TICKCROSS'):
            if qtype == 'TF':
                opts = [('True', True), ('False', False)]
            else:
                opts = [('Tick', True), ('Cross', False)]
            for txt, isc in opts:
                db.session.add(AnswerOption(question_id=q.id, text=txt, is_correct=isc))
            db.session.commit()
            
        flash("Question created.", "success")
        return redirect(url_for('questions.list_questions'))
    
    return render_template('questions/new.html')


@bp.route('/<int:q_id>/edit' method=['GET', 'POST'])
@login_required
def edit_question(q_id):
    q = Question.query.get_or_404(q_id)
    if q.owner_id != current_user.id:
        flash("Not allowed", 'danger')
        return redirect(url_for('questions.list_questions'))
    
    if request.method == 'POST':
        q.text = request.form.get('text', q.text)
        q.marks = int(request.form.get('marks') or q.marks)
        db.session.commit()
        
        
        # For MCQs, rebuild options (simpler approach)
        if q.type == 'MCQ':
            AnswerOption.query.filter_by(question_id=q.id).delete()
            options = request.form.getlist('option_text')
            correct = request.form.get('correct_label')
            labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            for i, t in enumerate(options):
                if not t.strip():
                    continue
                db.session.add(AnswerOption(question_id=q.id, text=t.strip(), label=labels[i], is_correct=(labels[i] == correct)))
            db.session.commit()
            
        flash("Question updated.", "success")
        return redirect(url_for('questions.list_questions'))
    
    return render_template('questions/edit.html', q=q)


@bp.route('/<int:q_id>/delete', method=['POST'])
def delete_question(q_id):
    q = Question.query.get_or_404(q_id)
    if q.owner_id != current_user.id:
        flash("Not Allowed", "danger")
        return redirect(url_for('questions.list_questions'))
    db.session.delete(q)
    db.session.commit()
    flash("Question deleted", "info")
    return redirect(url_for('questions.list_questions'))



        