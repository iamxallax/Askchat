import openai

# Set up OpenAI API credentials
openai.api_key = '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'

game_state = {
    'current_room': 'start',
    'inventory': [],
    'end_game': False
}

def generate_room(room_name):
    response = openai.Completion.create(
        prompt=f"Generate a description and options for the {room_name} room.",
        max_tokens=200,
        model="gpt-3.5-turbo"
    )
    generated_text = response.choices[0].text.strip()
    description, options = generated_text.split("Options:")
    return description.strip(), options.strip()

# Update room descriptions and options
for room_name in game_state.keys():
    description, options = generate_room(room_name)
    game_state[room_name] = {
        'description': description,
        'options': options
    }

# Define game loop
while not game_state['end_game']:
    room = game_state[game_state['current_room']]
    print(room['description'])
    print('Options: ' + room['options'])

    user_input = input('What do you want to do? ')

    # Use OpenAI API to generate response based on user input
    response = openai.Completion.create(
        prompt=f"In the {game_state['current_room']} room, {user_input}",
        max_tokens=50,
        model="gpt-3.5-turbo"
    )
    action = response.choices[0].text.strip()

    # Check if user input matches available actions
    if action in room['options']:
        game_state['current_room'] = action
    elif action in room['description']:
        game_state['inventory'].append(action)
        room['description'].remove(action)
    else:
        print('Invalid action. Please try again.')

    # Check if game is over
    if game_state['current_room'] == 'exit' or 'treasure' in game_state['inventory']:
        game_state['end_game'] = True

print('Game Over!')