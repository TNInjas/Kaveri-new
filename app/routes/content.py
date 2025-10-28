from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from datetime import datetime
from app.models.User import User
from app.models.profile import Profile
from app.models.Understanding import Understanding
from app.prompts.content_prompt import Content_prompt
from app.services.content_gen_service import Content_service

content_bp = Blueprint('content', __name__)

@content_bp.route('/chat')
def chat_interface():
    if 'user_id' not in session:
        flash('Please log in to access the chat', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    try:
        user = User.query.get(user_id)
        profile = Profile.query.filter_by(user_id=user_id).first()
        understanding = Understanding.query.filter_by(user_id=user_id).first()
        
        if not profile or not understanding:
            flash('Please complete your assessment first', 'info')
            return redirect(url_for('ass.assignment'))
        
        # Initialize conversation history if not exists
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        return render_template('chat.html', 
                             username=user.username,
                             has_profile=True,
                             history_count=len(session['conversation_history']))
        
    except Exception as e:
        print(f"Chat interface error: {e}")
        flash('Error loading chat interface', 'error')
        return redirect(url_for('dash.dashboard'))

@content_bp.route('/api/send_message', methods=['POST'])
def send_message():
    """
    API endpoint to send message and get AI response with memory
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in'}), 401
    
    user_id = session['user_id']
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Initialize conversation history in session if not exists
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        # Get user data from database
        user = User.query.get(user_id)
        understanding = Understanding.query.filter_by(user_id=user_id).first()
        
        if not user or not understanding:
            return jsonify({'error': 'User profile not found. Please complete assessment.'}), 400
        
        # Build conversation context from history
        conversation_context = _build_conversation_context(session['conversation_history'])
        
        # Build personalized prompt with conversation context
        personalized_prompt = Content_prompt(
            name=user.username,
            strengths=understanding.strengths,
            learning_pace=understanding.learning_pace,
            motivation_factors=understanding.motivation_factors,
            cognitive_level=understanding.cognitive_level,
            problem_solving_style=understanding.problem_solving_style,
            message=user_message
        )
        
        # Enhance prompt with conversation context
        enhanced_prompt = f"{personalized_prompt}\n\nCONVERSATION CONTEXT:\n{conversation_context}\n\nPlease continue the conversation naturally, building on previous messages."
        
        # Generate AI response
        content_service = Content_service()
        raw_response = content_service.send_request(enhanced_prompt)
        
        if raw_response:
            parsed_response = content_service.parse_ai_response(raw_response)
            
            # Update conversation history in session
            session['conversation_history'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.utcnow().isoformat()
            })
            session['conversation_history'].append({
                'role': 'assistant', 
                'content': parsed_response['content'],
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Keep only last 20 messages (10 exchanges) to prevent session from getting too large
            if len(session['conversation_history']) > 20:
                session['conversation_history'] = session['conversation_history'][-20:]
            
            # Mark session as modified to ensure changes are saved
            session.modified = True
            
            return jsonify({
                'success': True,
                'user_message': user_message,
                'ai_response': parsed_response['content'],
                'metadata': parsed_response['metadata'],
                'structured_data': parsed_response['structured_data'],
                'history_length': len(session['conversation_history'])
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to get response from AI service'
            }), 500
            
    except Exception as e:
        print(f"Send message error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@content_bp.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    """
    Get user's current chat history from session
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in'}), 401
    
    history = session.get('conversation_history', [])
    
    return jsonify({
        'success': True,
        'history': history,
        'total_messages': len(history)
    })

@content_bp.route('/api/clear_chat', methods=['POST'])
def clear_chat():
    """
    Clear current conversation history from session
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in'}), 401
    
    session.pop('conversation_history', None)
    session.modified = True
    
    return jsonify({
        'success': True,
        'message': 'Chat history cleared successfully',
        'history_length': 0
    })

def _build_conversation_context(history):
    """
    Build conversation context from history for the AI prompt
    """
    if not history:
        return "This is the start of the conversation. No previous messages."
    
    # Get last 10 messages (5 exchanges) for context
    recent_messages = history[-10:] if len(history) > 10 else history
    
    context = "Recent conversation history:\n"
    for i, msg in enumerate(recent_messages):
        role = "User" if msg['role'] == 'user' else "Assistant"
        # Shorten very long messages to prevent token overflow
        content = msg['content']
        if len(content) > 300:
            content = content[:300] + "..."
        context += f"{role}: {content}\n"
    
    return context