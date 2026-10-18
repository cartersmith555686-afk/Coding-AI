import os
import random
import math
# Added render_template to imports
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Global variables to store our custom agent's brain data
model_vocab = []
char_to_idx = {}
idx_to_char = {}
training_context = ""

# Base system templates
DEFAULT_PROMPT = "You are Claude Fable 5.1, an elite programming assistant."
DEFAULT_DATA = "function add(a, b) { return a + b; }\nfunction sub(a, b) { return a - b; }"

@app.route('/')
def home():
    # FIXED: Uses native Flask templates to read index.html from the templates/ folder automatically
    return render_template('index.html')

@app.route('/train', methods=['POST'])
def train():
    global model_vocab, char_to_idx, idx_to_char, training_context
    data = request.json or {}
    
    system_prompt = data.get('system_prompt', '').strip() or DEFAULT_PROMPT
    dataset_text = data.get('dataset_text', '').strip() or DEFAULT_DATA
    
    # Merge custom persona prompt rules into the training data stream
    training_context = f"{system_prompt}\n{dataset_text}"
    
    if len(training_context) < 5:
        return jsonify({"status": "error", "message": "Dataset too short!"}), 400
        
    # Build vocabulary mappings
    model_vocab = list(set(training_context))
    char_to_idx = {char: i for i, char in enumerate(model_vocab)}
    idx_to_char = {i: char for i, char in enumerate(model_vocab)}
    
    return jsonify({"status": "success", "message": f"Successfully compiled persona with {len(model_vocab)} unique characters."})

@app.route('/generate', methods=['POST'])
def generate():
    global model_vocab, char_to_idx, idx_to_char, training_context
    if not model_vocab:
        return jsonify({"status": "error", "message": "Model not trained yet!"}), 400
        
    data = request.json or {}
    user_prompt = data.get('prompt', '').strip()
    strictness = int(data.get('strictness', 50))
    
    # Map strictness slider values into temperature parameters
    if strictness < 35:
        temperature = 1.5  # Less strict/wild
        min_confidence = 0.0
    elif strictness <= 70:
        temperature = 0.7  # Balanced
        min_confidence = 0.1
    else:
        temperature = 0.2  # Max strict/rigid
        min_confidence = 0.4

    # Extract initial seed token from the custom chat message
    seed_char = user_prompt if user_prompt and user_prompt in char_to_idx else random.choice(model_vocab)
    generated_text = seed_char
    current_char = seed_char

    # Simulated server-side inference loop based on relative text frequencies
    for _ in range(180):
        # Look for instances of current token inside the training context matrix
        positions = [i for i, char in enumerate(training_context[:-1]) if char == current_char]
        
        if not positions:
            break
            
        # Compile counts for what character usually follows next
        next_chars = [training_context[pos + 1] for pos in positions]
        weights = {c: next_chars.count(c) / len(next_chars) for c in set(next_chars)}
        
        # Apply Temperature scale to adjust strictness
        adjusted_weights = {}
        for c, w in weights.items():
            try:
                adjusted_weights[c] = math.exp(math.log(w + 1e-7) / temperature)
            except ValueError:
                adjusted_weights[c] = w
                
        total_w = sum(adjusted_weights.values())
        if total_w == 0:
            break
            
        # Select next character
        choices = list(adjusted_weights.keys())
        probabilities = [adjusted_weights[c] / total_w for c in choices]
        
        # Strictness check: Enforce confidence cutoff
        if max(probabilities) < min_confidence:
            generated_text += "\n\n[Halted: Confidence falls below guardrails threshold]"
            break
            
        next_picked = random.choices(choices, weights=probabilities)[0]
        generated_text += next_picked
        current_char = next_picked

    return jsonify({"status": "success", "output": generated_text})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
