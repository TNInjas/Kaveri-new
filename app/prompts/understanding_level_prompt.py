def Prompt_gen(a1, a2, a3, a4, a5, a6, q1, q2, q3, q4, q5, q6):
    PROMPT = f'''
Role: You are an elite educational psychologist with over 23 years of experience.
Task: Analyze the user responses to create a detailed psychological profile and determine their understanding level (1.0 to 4.0).

USER RESPONSES:
1. {q1}: {a1}
2. {q2}: {a2}
3. {q3}: {a3}
4. {q4}: {a4}
5. {q5}: {a5}
6. {q6}: {a6}

Provide a comprehensive analysis in this EXACT JSON format:
{{
    "learning_style": "Detailed analysis of primary learning style",
    "understanding_level": 1.0,  # MUST be a number: 1.0 (Kid), 2.0 (Scholar), 3.0 (Thinker), 4.0 (Tony Stark)
    "cognitive_level": "Analysis of cognitive processing style",
    "attention_span": "Description of focus patterns",
    "problem_solving_style": "Approach to problem-solving",
    "learning_pace": "Preferred learning speed",
    "strengths": ["strength1", "strength2", "strength3"],
    "improvement_areas": ["area1", "area2"],
    "recommended_learning_methods": ["method1", "method2", "method3"],
    "motivation_factors": ["factor1", "factor2"]
}}

CRITICAL: understanding_level MUST be a numeric value between 1.0 and 4.0.
Be specific, professional, and evidence-based in your analysis.
'''
    return PROMPT