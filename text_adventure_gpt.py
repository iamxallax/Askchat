import netrc
import json

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


def submit_conversation(conversation):

    # pprint.pprint(conversation)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation
    )
    
    # return a string containing the content
    return response['choices'][0]['message']['content']    
    

def create_summary():
    conversation = [{'role': 'system', 'content': 'You are a dungeon master that must lead players through an action-packed short adventure'},
                    {'role': 'user', 'content': 'Create a one paragraph D&D adventure.'},
                    {'role': 'assistant', 'content': "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out. But their problems don't end there. The temple is haunted by the ghost of an ancient High Priestess, who haunts the players' dreams and demands to be set free. If the players don't appease her, they'll never make it out alive. Along the way, they uncover a plot by a rival faction of merfolk who seek to destroy the temple and exploit the ancient artifacts it protects. The players must choose between solving the temple's puzzles, satisfying the ghost's demands, and stopping the rival faction from achieving their goal."},
                    ]
    adventure = askgpt('Now create another one with a similar structure but a different theme and plot. Include details about the setting and the starting point of the story.', conversation=conversation)
    return adventure['message']


def get_next_step(conversation):
    
    prompt = '''The response to this prompt must be a valid json object. Given the adventure above, first provide a few detailed sentences describing the next step in the adventure above. This corresponds to the attribute "next_step" in the json-formatted response. Then provide 2-4 options the player might take next. Each option should consist only of an action that the player might choose and should not include additional narrative. Each option should have "Skill [example_number] - " where the example_number is a number between 1 and 10, that indicates how difficult that action would be. The number should rarely by a 9 or 10, as those are reserved to actions lik e seducing dragons or other actions of that difficulty. Assume the player knows nothing about the plot, so describe in detail how they got from point A to point B. These options correspond to the json object "options"'''
    
    prompt += f'''It is extremely important that the entire story arc is no more than 25 steps, with an obvious climax and a resolution. Limit the character's options to choices that advance the plot. The user has already taken one or more steps; Make sure the new step incorporates the actions of the user's previous steps.'''
        
    prompt += ' The entire response to this prompt should be formatted as a json object using the schema {"next_step": "...", "options": ["Skill [number] - option 1", "Skill [number] - option 2", ...]}. The entire response MUST be a valid json object.'

    attempt = 1
    while True:
        try:
            #output = submit_conversation(conversation + [
            #    {'role': 'user', 'content': prompt}
            #])
            output = askgpt(prompt, conversation=conversation)['message']
            # print(output)
            return json.loads(output)
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
            text = d[response]
            text = text.replace("Skill ", '')
            skill_level = int(text.split(' - ')[0])
            if grade_roleplay(ask_description()) >= skill_level:
                success = True
            else:
                success = False
            return (d[response], success)
        
def ask_description():
    response = input('Describe in detail how you would go about doing this action:\n\n')
    return response

def save_to_file(filename, text):
    with open(filename, 'w') as f:
        f.write(text + '\n')

def grade_roleplay(string):
    if string == 'BYPASS':
        return 10
    prompt = 'I need you to grade this description from 1 to 10. it should be graded by how creative and descriptive it is. You should go easy, giving a 10 to a descriptive one, but be harsh if it is uncreative. For example, "I attack the monster" would get a grade of 1, while "I swing my sword in a delicate dance, slashing and cutting everywhere. My flurry of blows is dazzling as my sword shines with red and silver" would get a 10. Only respond with a number from 1 to 10. Here is the description I need you to grade: ' + string
    while True:
        try:
            output = askgpt(prompt)
            print(output)
            return int(output['message'])
        except ValueError:
            print('The AI did it wrong...')

def main():

    """Create the elements of the converstion that should be repeated with each prompt before the game loop, then add new prompts each iteration of the while loop."""

    adventure = "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out. But their problems don't end there. The temple is haunted by the ghost of an ancient High Priestess, who haunts the players' dreams and demands to be set free. If the players don't appease her, they'll never make it out alive. Along the way, they uncover a plot by a rival faction of merfolk who seek to destroy the temple and exploit the ancient artifacts it protects. The players must choose between solving the temple's puzzles, satisfying the ghost's demands, and stopping the rival faction from achieving their goal."

    intro = "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out"

    # adventure = create_summary()
    # intro = separate_summary(adventure)

    #print(adventure)
    print(intro)

    conversation = [{'role': 'system', 
                     'content': 'You are a fine tuned general language model that follows the prompt exactly.'},
                    {'role': 'assistant', 
                     'content': adventure}]

    round = 1
    running = True
    while running:
        response = get_next_step(conversation)
        description = response['next_step']
        print(f'{round=}')
        print(description + '\n')
        choice, success = ask(response['options'])
        print(success)
        
        if round == 10:
            print('\n' * 3, 'Here is the actual plot: "' + adventure + '"')
            exit()

        conversation.append({'role': 'assistant', 'content': description})
        conversation.append({'role': 'user', 'content': choice})
        if not success:
            conversation.append({'role': 'user', 'content': "The user did not succeed in completing this action."})
        round += 1



# ChatGPT_model = "gpt-4"  
#main()