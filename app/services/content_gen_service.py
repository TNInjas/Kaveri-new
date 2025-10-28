API_KEY = 'IcyxRheXstLykYWjQ7QCTG3sp8ocb1KN'
MODEL = 'mistral-large-2411'
URL = 'https://api.mistral.ai/v1/chat/completions'

class Content_service:
    def __init__(self, key=API_KEY, url=URL, model=MODEL):
        self.key = key
        self.url = url
        self.model = model

    def send_request(self, content):
        try:
            import requests
            import json
            
            response = requests.post(
                url=self.url,
                headers={
                    'Authorization': f'Bearer {self.key}',
                    'Content-Type': 'application/json', 
                    'HTTP-Referer': 'http://localhost:5000', 
                    'X-Title': 'Kaveri.ai Learning Assistant'
                },
                data=json.dumps({
                    'model': self.model,
                    'messages': [
                        {'role': 'user', 'content': content}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 4000,  
                    'top_p': 0.9,
                    'frequency_penalty': 0.1,  
                    'presence_penalty': 0.1    
                }),
                timeout=30 
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f'API error: {response.status_code} {response.text}')
                return None
        except requests.exceptions.Timeout:
            print("Request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except KeyError as e:
            print(f"Unexpected response format: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def parse_ai_response(self, response_text):
        try:
            import re
            
            if not response_text:
                return self._get_error_response("Empty response from AI")
            
            cleaned_text = self._clean_response_text_preserve_code(response_text)
            structured_data = self._extract_structured_data(cleaned_text)
            response_analysis = self._analyze_response(cleaned_text)
            
            parsed_response = {
                'content': cleaned_text,
                'structured_data': structured_data,
                'metadata': {
                    'response_type': response_analysis['type'],
                    'content_quality': response_analysis['quality'],
                    'has_questions': response_analysis['has_questions'],
                    'has_examples': response_analysis['has_examples'],
                    'has_code': response_analysis['has_code'],  
                    'word_count': len(cleaned_text.split()),
                    'paragraph_count': cleaned_text.count('\n\n') + 1
                },
                'success': True
            }
            
            return parsed_response
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._get_error_response(f"Error processing response: {str(e)}")

    def _clean_response_text_preserve_code(self, text):
        import re
        
        text = re.sub(r'(?<!\n)\n(?!\n)(?![`])', ' ', text)
        
        lines = text.split('\n')
        cleaned_lines = []
        in_code_block = False
        
        for line in lines:
            if '```' in line:
                in_code_block = not in_code_block
                cleaned_lines.append(line)
            elif not in_code_block:
                line = re.sub(r'([.!?])([A-Z])', r'\1 \2', line)
                line = re.sub(r'[*_#]', '', line)
                cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text.strip()

    def _clean_response_text(self, text):
        import re
        
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        text = re.sub(r'[*_`#]', '', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text

    def _extract_structured_data(self, text):
        import re
        
        structured_data = {}
        sections = {}
        lines = text.split('\n')
        current_section = "main"
        section_content = []
        
        for line in lines:
            if (len(line.strip()) < 100 and 
                not line.strip().endswith('.') and 
                not line.strip().endswith('?') and
                len(line.strip()) > 0 and
                line.strip() not in ['**', '*', ''] and
                '```' not in line):  
                
                if section_content and current_section != "main":
                    sections[current_section] = '\n'.join(section_content).strip()
                
                current_section = line.strip()
                section_content = []
            else:
                section_content.append(line)

        if section_content:
            sections[current_section] = '\n'.join(section_content).strip()
        
        structured_data['sections'] = sections
        
        questions = re.findall(r'([^.!?]*\?+)', text)
        structured_data['questions'] = [q.strip() for q in questions if len(q.strip()) > 10]

        examples = re.findall(r'(?:^|\n)[•\-*\d+\.]\s*([^\n]+)', text)
        structured_data['examples'] = [ex.strip() for ex in examples]
        
        code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)```', text)
        structured_data['code_blocks'] = [code.strip() for code in code_blocks]
        
        sentences = re.split(r'[.!?]+', text)
        key_points = [s.strip() for s in sentences if 20 < len(s.strip()) < 150]
        structured_data['key_points'] = key_points[:5] 
        
        return structured_data

    def _analyze_response(self, text):
        analysis = {
            'type': 'explanation',
            'quality': 'good',
            'has_questions': False,
            'has_examples': False,
            'has_code': False  
        }
        
        if '```' in text:
            analysis['has_code'] = True
            analysis['type'] = 'code_example'
        
        if '?' in text:
            analysis['has_questions'] = True
        
        example_indicators = ['for example', 'for instance', 'such as', 'e.g.', 'like']
        if any(indicator in text.lower() for indicator in example_indicators):
            analysis['has_examples'] = True
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['step', 'process', 'procedure', 'how to']):
            analysis['type'] = 'tutorial'
        elif any(word in text_lower for word in ['question', 'what do you think', 'your opinion']):
            analysis['type'] = 'discussion'
        elif any(word in text_lower for word in ['summary', 'conclusion', 'in summary']):
            analysis['type'] = 'summary'
        elif any(word in text_lower for word in ['compare', 'versus', 'vs', 'difference']):
            analysis['type'] = 'comparison'
        
        programming_languages = ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'html', 'css', 'sql']
        if any(lang in text_lower for lang in programming_languages):
            analysis['type'] = 'programming'
        
        word_count = len(text.split())
        paragraph_count = text.count('\n\n') + 1
        
        if word_count < 50:
            analysis['quality'] = 'poor'
        elif word_count > 500 and paragraph_count > 3:
            analysis['quality'] = 'excellent'
        elif word_count > 200:
            analysis['quality'] = 'good'
        else:
            analysis['quality'] = 'adequate'
        
        return analysis

    def _get_error_response(self, error_message):
        return {
            'content': f"I apologize, but I encountered an issue while generating the response. {error_message}\n\nPlease try asking your question again or rephrase it.",
            'structured_data': {},
            'metadata': {
                'response_type': 'error',
                'content_quality': 'poor',
                'has_questions': False,
                'has_examples': False,
                'has_code': False,
                'word_count': 0,
                'paragraph_count': 1
            },
            'success': False
        }

    def generate_chat_response(self, user_message, conversation_history=None):
        prompt = self._build_chat_prompt(user_message, conversation_history)
        
        raw_response = self.send_request(prompt)
        
        if raw_response:
            return self.parse_ai_response(raw_response)
        else:
            return self._get_error_response("Failed to get response from AI service")

    def _build_chat_prompt(self, user_message, conversation_history=None):
        base_prompt = """
        You are a helpful, engaging learning assistant. Provide clear, informative responses that are easy to understand.
        When users ask for code, provide complete, runnable code examples with proper formatting using code blocks.
        """
        
        if conversation_history:
            history_context = "\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:
                role = "User" if msg.get('role') == 'user' else "Assistant"
                history_context += f"{role}: {msg.get('content', '')}\n"
            
            base_prompt += history_context + "\n"
        
        base_prompt += f"Current user message: {user_message}\n\nPlease provide a helpful response:"
        
        return base_prompt