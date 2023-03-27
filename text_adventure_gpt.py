import netrc
import json

import openai

__, __, api_key = netrc.netrc().authenticators('openai')

openai.api_key = api_key

def askgpt(question, background=None, conversation=None):
    if conversation == None:
        conversation = []
        if background:
            conversation.append({"role": "system", "content": background})
    conversation.append({'role': 'user', 'content': question})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    message = response['choices'][0]['message']
    conversation.append(message)
    return {'conversation': conversation, 'message': message['content']}

def create_summary():
    conversation = [{'role': 'system', 'content': 'You are a dungeon master that must lead players through an action-packed short adventure'},
                    {'role': 'user', 'content': 'Create a one paragraph D&D adventure.'},
                    {'role': 'assistant', 'content': "As the players enter the bustling city, they are approached by a hooded figure who hands them a mysterious note. The note is an invitation to a secret underground fighting tournament, where the winner will be rewarded with a rare and powerful magical item. The tournament takes place in a labyrinthine maze, where the players must battle other formidable opponents to reach the end. But the maze is filled with traps and puzzles that must be solved to progress. As they fight their way through, the players discover that the tournament is run by a shadowy organization with sinister motives. They must decide whether to continue on and claim the prize, or to expose the organization's secrets and stop them once and for all."},
                    ]
    adventure = askgpt('Now create another one is vastly different to the first.', conversation=conversation)
    return adventure['message']

def get_next_step(adventure, steps_taken=None):
    prompt = '''This is the summary of an adventure. Start at the vevry start of the adventure. Provide a few detailed sentences describing the next step in the adventure. Then provide 2-4 options the player might take next. Each option should consist only of an option that the player might choose and should not include additional narrative. The response should be formatted as a json object using the schema {next_step: "...", options: ["option 1", "option 2", ...]}
    '''    

    if steps_taken:
        prompt += "The user has already taken one or more steps. here is the description of the setting and the steps the user took. make sure the new step progresses the story and incorporates the actions of the user's previous steps: "
        for (step, chosen_option) in steps_taken:
            prompt += f"Step {steps_taken.index((step, chosen_option)) + 1}: {step}. Chosen action: {chosen_option}."
    prompt += "Here is the adventure: " + adventure
    while True:
        try:
            output = askgpt(prompt)
            return json.loads(output['message'])
        except json.decoder.JSONDecodeError as err:
            print(err)

def ask(options):
    d = {str(i): opt for i, opt in enumerate(options, 1)}
    while True:
        for i, option in d.items():
            print(f'{i}: {option}')
        response = input('choose a number: ').strip()
        if response in d:
            return d[response]

adventure = create_summary()
print(adventure)

running = True
previous_steps = []
while running:
    response = get_next_step(adventure=adventure, steps_taken=previous_steps)
    description = response['next_step']
    print(description)
    choice = ask(response['options'])
    previous_steps.append((description, choice))
