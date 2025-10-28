from app.services.content_gen_service import Content_service


class Assignment_service:
    def __init__(self):
        self.content_service = Content_service()

    def send_request(self, prompt_text):
        return self.content_service.send_request(prompt_text)

    def parse_ai_response(self, response_text):
        parsed = self.content_service.parse_ai_response(response_text)
        # Map to the fields expected by routes/assignment.py
        return self._map_parsed_to_profile(parsed)

    def get_fallback_analysis(self):
        # Reasonable defaults used when AI is unavailable
        return {
            'learning_style': 'visual',
            'cognitive_level': 'intermediate',
            'attention_span': 'moderate',
            'problem_solving_style': 'analytical',
            'learning_pace': 'steady',
            'strengths': ['pattern recognition', 'structured thinking'],
            'improvement_areas': ['applied examples', 'practice frequency'],
            'recommended_learning_methods': ['diagrams', 'worked examples', 'spaced repetition'],
            'motivation_factors': ['clear goals', 'visible progress']
        }

    def _map_parsed_to_profile(self, parsed):
        if not parsed or not parsed.get('success'):
            return self.get_fallback_analysis()

        text = parsed.get('content', '')
        # Very light heuristic mapping until a stricter schema is enforced
        text_lower = text.lower()
        learning_style = 'visual' if 'diagram' in text_lower or 'visual' in text_lower else (
            'auditory' if 'audio' in text_lower or 'listen' in text_lower else 'reading/writing'
        )

        result = {
            'learning_style': learning_style,
            'cognitive_level': 'intermediate',
            'attention_span': 'moderate',
            'problem_solving_style': 'analytical' if 'step' in text_lower else 'intuitive',
            'learning_pace': 'steady',
            'strengths': parsed.get('structured_data', {}).get('key_points', [])[:3] or ['comprehension'],
            'improvement_areas': ['practice variety'],
            'recommended_learning_methods': ['worked examples', 'practice problems'],
            'motivation_factors': ['progress tracking']
        }

        return result