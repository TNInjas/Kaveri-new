from flask import Blueprint, redirect, render_template, session, url_for, flash, request
from app import db
from app.models.User import User
from app.models.profile import Profile
from app.models.Understanding import Understanding
from app.prompts.understanding_level_prompt import Prompt_gen
from app.services.assignment_service import Assignment_service
from datetime import datetime

ass_bp = Blueprint('ass', __name__)

@ass_bp.route('/assignment', methods=['POST', 'GET'])
def assignment():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        Q1_answer = request.form.get('Q1_answer')
        Q2_answer = request.form.get('Q2_answer')
        Q3_answer = request.form.get('Q3_answer')
        Q4_answer = request.form.get('Q4_answer')
        Q5_answer = request.form.get('Q5_answer')
        Q6_answer = request.form.get('Q6_answer')

        Questions = {
            'Q1': 'When learning complex new information, what approach works best for you?',
            'Q2': 'How do you typically approach solving difficult problems?',
            'Q3': 'What type of learning environment helps you concentrate best?',
            'Q4': 'When you encounter challenging concepts, what is your immediate reaction?',
            'Q5': 'How do you prefer to receive feedback on your work?',
            'Q6': 'What motivates you most when learning something new?'
        }

        if not all([Q1_answer, Q2_answer, Q3_answer, Q4_answer, Q5_answer, Q6_answer]):
            flash('All questions are required', 'error')
            return render_template('assignment.html')
        
        try:
            prompt = Prompt_gen(Q1_answer, Q2_answer, Q3_answer, Q4_answer, Q5_answer, Q6_answer,
                              Questions['Q1'], Questions['Q2'], Questions['Q3'], Questions['Q4'],
                              Questions['Q5'], Questions['Q6'])
            
            assignment_service = Assignment_service()
            ai_response = assignment_service.send_request(prompt)

            if not ai_response:
                flash('AI service temporarily unavailable. Using default profile.', 'warning')
                ai_analysis = assignment_service.get_fallback_analysis()
            else:
                ai_analysis = assignment_service.parse_ai_response(ai_response)

            existing_profile = Profile.query.filter_by(user_id=user_id).first()
            existing_understanding = Understanding.query.filter_by(user_id=user_id).first()

            if existing_profile and existing_understanding:
                existing_profile.Q1_answer = Q1_answer
                existing_profile.Q2_answer = Q2_answer
                existing_profile.Q3_answer = Q3_answer
                existing_profile.Q4_answer = Q4_answer
                existing_profile.Q5_answer = Q5_answer
                existing_profile.Q6_answer = Q6_answer
                existing_profile.updated_at = datetime.utcnow()
                
                existing_understanding.learning_style = ai_analysis.get('learning_style', '')
                existing_understanding.cognitive_level = ai_analysis.get('cognitive_level', '')
                existing_understanding.attention_span = ai_analysis.get('attention_span', '')
                existing_understanding.problem_solving_style = ai_analysis.get('problem_solving_style', '')
                existing_understanding.learning_pace = ai_analysis.get('learning_pace', '')
                existing_understanding.strengths = ', '.join(ai_analysis.get('strengths', []))
                existing_understanding.improvement_areas = ', '.join(ai_analysis.get('improvement_areas', []))
                existing_understanding.recommended_learning_methods = ', '.join(ai_analysis.get('recommended_learning_methods', []))
                existing_understanding.motivation_factors = ', '.join(ai_analysis.get('motivation_factors', []))
                existing_understanding.updated_at = datetime.utcnow()
                
                flash('Profile updated successfully! Your learning assistant is now even more personalized.', 'success')
                
            else:
                profile = Profile(
                    user_id=user_id,
                    Q1_answer=Q1_answer,
                    Q2_answer=Q2_answer,
                    Q3_answer=Q3_answer,
                    Q4_answer=Q4_answer,
                    Q5_answer=Q5_answer,
                    Q6_answer=Q6_answer
                )

                understanding = Understanding(
                    user_id=user_id,
                    learning_style=ai_analysis.get('learning_style', ''),
                    cognitive_level=ai_analysis.get('cognitive_level', ''),
                    attention_span=ai_analysis.get('attention_span', ''),
                    problem_solving_style=ai_analysis.get('problem_solving_style', ''),
                    learning_pace=ai_analysis.get('learning_pace', ''),
                    strengths=', '.join(ai_analysis.get('strengths', [])),
                    improvement_areas=', '.join(ai_analysis.get('improvement_areas', [])),
                    recommended_learning_methods=', '.join(ai_analysis.get('recommended_learning_methods', [])),
                    motivation_factors=', '.join(ai_analysis.get('motivation_factors', []))
                )

                db.session.add(profile)
                db.session.add(understanding)
                flash('Profile created successfully!', 'success')

            user.last_assessment = datetime.utcnow()
            db.session.commit()
            
            return redirect(url_for('dash.dashboard'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Assignment error: {e}")
            flash('Error occurred during assessment. Please try again.', 'error')
            return render_template('assignment.html')

    existing_profile = Profile.query.filter_by(user_id=user_id).first()
    
    if existing_profile and not user.needs_reassessment():
        return redirect(url_for('dash.dashboard'))
    
    return render_template('assignment.html')