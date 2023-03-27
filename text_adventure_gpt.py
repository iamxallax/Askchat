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
                    {'role': 'assistant', 'content': "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out. But their problems don't end there. The temple is haunted by the ghost of an ancient High Priestess, who haunts the players' dreams and demands to be set free. If the players don't appease her, they'll never make it out alive. Along the way, they uncover a plot by a rival faction of merfolk who seek to destroy the temple and exploit the ancient artifacts it protects. The players must choose between solving the temple's puzzles, satisfying the ghost's demands, and stopping the rival faction from achieving their goal."},
                    ]
    adventure = askgpt('Now create another one with a similar structure but a different theme and plot. Include details about the setting and the starting point of the story.', conversation=conversation)
    return adventure['message']

def get_next_step(adventure, steps_taken=None):
    prompt = '''Provide a few detailed sentences describing the next step in the adventure. Then provide 2-4 options the player might take next. Each option should consist only of an option that the player might choose and should not include additional narrative. The response should be formatted as a json object using the schema {next_step: "...", options: ["option 1", "option 2", ...]}. The story should be no more than 10 steps, with an obvious climax and a resolution.
    '''    

    if steps_taken:
        prompt += "The user has already taken one or more steps. here is the description of the setting and the steps the user took. Make sure the new step progresses the story and incorporates the actions of the user's previous steps: "
        for (step, chosen_option) in steps_taken:
            prompt += f"Step {steps_taken.index((step, chosen_option)) + 1}: {step}. Chosen action: {chosen_option}. "
    prompt += "Here is the adventure: " + adventure
    while True:
        try:
            output = askgpt(prompt)
            print(output)
            return json.loads(output['message'])
        except json.decoder.JSONDecodeError as err:
            print(err)

def separate_summary(summary):
    output = askgpt('I need you to separate the beginning of this story from the rest. The beginning should include the setting and the actions that happen immediatly. Only respond with the separated beginning introduction. Here is the story: ' + summary)
    return output['message']

def ask(options):
    d = {str(i): opt for i, opt in enumerate(options, 1)}
    while True:
        for i, option in d.items():
            print(f'{i}: {option}')
        response = input('choose a number: ').strip()
        if response in d:
            return d[response]

adventure = create_summary()
intro = separate_summary(adventure)
print(adventure)
print(intro)

running = True
previous_steps = []
round = 1
while running:
    response = get_next_step(adventure=adventure if round != 1 else intro, steps_taken=previous_steps)
    description = response['next_step']
    print(description)
    choice = ask(response['options'])
    previous_steps.append((description, choice))
    round += 1
