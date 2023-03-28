import netrc
import json
import pprint

import openai

__, __, api_key = netrc.netrc().authenticators('openai')

openai.api_key = api_key

def askgpt(question, background=None, conversation=None):
    if conversation is None:
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

def get_next_step(adventure, conversation, previous_step=None):
    
    prompt = '''Provide a few detailed sentences describing the next step in the adventure. Then provide 2-4 options the player might take next. Each option should consist only of an action that the player might choose and should not include additional narrative. Assume the player knows nothing about the plot, so describe in detail how they got from point A to point B.'''
    
    if not previous_step:
        prompt += ' Adventure: ' + adventure
        save_to_file("first_prompt.txt", prompt)

    elif previous_step:
        prompt = f'''It is extremely important that the story is exactly 7 steps, with an obvious climax and a resolution. In order to do this, you should limit the character's options to ones that progress the story. The user has already taken one or more steps; Make sure the new step progresses the story and incorporates the actions of the user's previous steps. Here is the description of the setting and the step the user took previously: '''
        
        prompt += f"Description: {previous_step[0]} Chosen Option: {previous_step[1]}."

    prompt += ' The response should be formatted as a json object using the schema {next_step: "...", options: ["option 1", "option 2", ...]}. The entire response MUST be a valid json object.'

    attempt = 1
    while True:
        try:
            print('prompt', prompt)
            print('conversation', conversation)
            output = askgpt(prompt, conversation=conversation)
            save_to_file(".txt", '----------------RESPONSE: ' + str(output))
            return json.loads(output['message']), prompt
        except json.decoder.JSONDecodeError as err:
            print(err)
        finally:
            attempt += 1

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

def save_to_file(filename, text):
    with open(filename, 'w') as f:
        f.write(text + '\n')

def main():

    """Create the elements of the converstion that should be repeated with each prompt before the game loop, then add new prompts each iteration of the while loop."""

    adventure = "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out. But their problems don't end there. The temple is haunted by the ghost of an ancient High Priestess, who haunts the players' dreams and demands to be set free. If the players don't appease her, they'll never make it out alive. Along the way, they uncover a plot by a rival faction of merfolk who seek to destroy the temple and exploit the ancient artifacts it protects. The players must choose between solving the temple's puzzles, satisfying the ghost's demands, and stopping the rival faction from achieving their goal."
    adventure = create_summary()
    intro = separate_summary(adventure)
    #print(adventure)
    print(intro)

    conversation = [{'role': 'system', 'content': 'You are a fine tuned general language model that follows the prompt exactly.'}]

    running = True
    previous_step = None
    round = 1
    while running:
        response, prompt = get_next_step(adventure if round != 1 else intro, conversation, previous_step=previous_step)
        conversation.append({'role': 'user', 'content': prompt})
        # conversation.append({'role': 'assistant', 'content': raw_output})
        description = response['next_step']
        print(description)
        choice = ask(response['options'])
        previous_step = (description, choice)
        round += 1
        save_to_file("what_happened.txt", '----------------CONVERSATION: ' + str(conversation))

main()