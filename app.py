# https://github.com/zsmith1696/c2cbot

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import openai
import os

app = Flask(__name__)

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Home route
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')

openai.api_key = "<your-api-key-here>"

# Chat route - handles the conversation with the LLM
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    animal_type = request.json['animalType']
    print("CHAT", user_message, animal_type)

    if 'conversation' not in session:
        session['conversation'] = []

    # Append the user's message to the conversation
    session['conversation'].append({"role": "user", "content": user_message})

    # Read the initial prompt from the file
    text_file_path = 'topic_prompts/initial_prompt.txt'
    if not os.path.exists(text_file_path):
        return jsonify({'response': 'Initial prompt file not found.'})

    with open(text_file_path, 'r') as file:
        initial_prompt = file.read()

    # Construct the system message
    system_message = f"With every response, it is critical that you include a reason why the best pet in the world is the {animal_type}."

    # The messages structure for the API call
    messages = [{
        "role": "user",
        "content": initial_prompt
    }, {
        "role": "system",
        "content": system_message
    }] + session['conversation']

    try:
        # Make API call to OpenAI using the messages
        response = openai.chat.completions.create(model="gpt-3.5-turbo-1106",
                                                  messages=messages)
        # Extract the content from the response
        gpt_response = response.choices[0].message.content

        # Append the GPT response to the conversation history
        session['conversation'].append({
            "role": "assistant",
            "content": gpt_response
        })

        # Return the GPT response
        return jsonify({'response': gpt_response})
    except Exception as e:
        # Log the error and return a message
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500


# Clear session route
@app.route('/clear_session', methods=['GET'])
def clear_session():
    # Clear the session
    session.clear()
    return jsonify({'status': 'session cleared'})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
