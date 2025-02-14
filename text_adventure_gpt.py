import netrc
import json
import random

import pygame
from pathlib import Path
import openai
from openai import OpenAI
__, __, api_key = netrc.netrc().authenticators('openai')

client = OpenAI(api_key=api_key)

pygame.init()
pygame.mixer.init()

def askgpt(question, background=None, conversation=None):
    if conversation is None:
        conversation = []
        if background:
            conversation.append({"role": "system", "content": background})


    conversation.append({'role': 'user', 'content': question})


    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation
    )
    message = response.choices[0].message.content
    conversation.append(message)
    conversation[-1][0]

    return {'conversation': conversation, 'message': message}

def read_out(text, voice="fable"):
    speech_file_path = Path(__file__).parent / f"read_out_text_adventure.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    response.stream_to_file(speech_file_path)

    pygame.mixer.music.load(speech_file_path)
    pygame.mixer.music.play() 

def create_summary():
    conversation = [{'role': 'system', 'content': 'You are a dungeon master that must lead players through an action-packed short adventure'},
                    {'role': 'user', 'content': 'Create a one paragraph D&D adventure.'},
                    {'role': 'assistant', 'content': "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out. But their problems don't end there. The temple is haunted by the ghost of an ancient High Priestess, who haunts the players' dreams and demands to be set free. If the players don't appease her, they'll never make it out alive. Along the way, they uncover a plot by a rival faction of merfolk who seek to destroy the temple and exploit the ancient artifacts it protects. The players must choose between solving the temple's puzzles, satisfying the ghost's demands, and stopping the rival faction from achieving their goal."},
                    ]
    adventure = askgpt('Now create another one with a similar structure but a different theme and plot. Include details about the setting and the starting point of the story.', conversation=conversation)
    return adventure['message']

def create_goal(adventure):
    adventure_preset = "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out. But their problems don't end there. The temple is haunted by the ghost of an ancient High Priestess, who haunts the players' dreams and demands to be set free. If the players don't appease her, they'll never make it out alive. Along the way, they uncover a plot by a rival faction of merfolk who seek to destroy the temple and exploit the ancient artifacts it protects. The players must choose between solving the temple's puzzles, satisfying the ghost's demands, and stopping the rival faction from achieving their goal."
    coversation = [{'role': 'user', 'content': 'I need an end goal that is not too hard to complete for D&D players. Your response should be 1 sentence long. Create an end goal for this story: ' + adventure_preset},
                   {'role': 'assistant', 'content': 'Defeating the rival clan, freeing the high priestess and/or escaping themselves.'}]
    goal = askgpt('Give me another goal but for a new story. Your response should be in the same format as before. New story: ' + adventure, conversation=coversation)
    


def get_next_step(conversation, goal):
    
    prompt = '''The response to this prompt must be a valid json object. Given the adventure above, first provide a few detailed sentences describing the next step in the adventure above. This corresponds to the attribute "next_step" in the json-formatted response. Then provide 2-4 options the player might take next. Each option should consist only of an action that the player might choose and should not include additional narrative. Assume the player knows nothing about the plot, so describe in detail how they got from point A to point B. These options correspond to the json object "options"'''
    
    prompt += f'''It is extremely important that the entire story arc is no more than 25 steps, with an obvious climax and a resolution. Limit the character's options to choices that advance the plot. Remember, the end goal of your D&D adventure is to lead the players through the climax, making sure they are {goal}. The user has already taken one or more steps; Make sure the new step incorporates the actions of the user's previous steps.'''
        
    prompt += ' The entire response to this prompt should be formatted as a json object using the schema {"next_step": "...", "options": ["x - option 1", "x - option 2", ...]}, where "x" is a skill level (between 2 and 12) of the action. An example of an options could be: "3 - Ask the mage for information". The entire response MUST be a valid json object.'

    attempt = 1
    while True:
        try:
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
            return (d[response])
        
def ask_description():
    response = input('Describe in detail how you would go about doing this action:\n\n')
    return response

def save_to_file(filename, text):
    with open(filename, 'w') as f:
        f.write(text + '\n')

def print_dice(numlist):
    DICE_ART = {
    1: (
        "┌─────────┐",
        "│         │",
        "│    ●    │",
        "│         │",
        "└─────────┘",
    ),
    2: (
        "┌─────────┐",
        "│  ●      │",
        "│         │",
        "│      ●  │",
        "└─────────┘",
    ),
    3: (
        "┌─────────┐",
        "│  ●      │",
        "│    ●    │",
        "│      ●  │",
        "└─────────┘",
    ),
    4: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│         │",
        "│  ●   ●  │",
        "└─────────┘",
    ),
    5: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│    ●    │",
        "│  ●   ●  │",
        "└─────────┘",
    ),
    6: (
        "┌─────────┐",
        "│  ●   ●  │",
        "│  ●   ●  │",
        "│  ●   ●  │",
        "└─────────┘",
    )}

    str_dice = ""
    for i in range(5):
        for z in numlist:
            str_dice += DICE_ART[z][i]
            str_dice += "   "
        str_dice += '\n'
    return str_dice



# def grade_roleplay(string):
#     if string == 'BYPASS':
#         return 10
#     prompt = 'I need you to grade this description from 1 to 10. it should be graded by how creative and descriptive it is. You should go easy, giving a 10 to a descriptive one, but be harsh if it is uncreative. For example, "I attack the monster" would get a grade of 1, while "I swing my sword in a delicate dance, slashing and cutting everywhere. My flurry of blows is dazzling as my sword shines with red and silver" would get a 10. Only respond with a number from 1 to 10. Here is the description I need you to grade: ' + string
#     while True:
#         try:
#             output = askgpt(prompt)
#             print(output)
#             return int(output['message'])
#         except ValueError:
#             print('The AI did it wrong...')

# def check_success(text, level):
#     text = text.replace("Skill ", '')
#     skill_level = int(text.split(' - ')[0])
#     if level >= skill_level:
#         return None
#     elif grade_roleplay(ask_description()) >= skill_level:
#         success = True
#     else:
#         success = False
#     return success

def main():

    """Create the elements of the converstion that should be repeated with each prompt before the game loop, then add new prompts each iteration of the while loop."""

    adventure = "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out. But their problems don't end there. The temple is haunted by the ghost of an ancient High Priestess, who haunts the players' dreams and demands to be set free. If the players don't appease her, they'll never make it out alive. Along the way, they uncover a plot by a rival faction of merfolk who seek to destroy the temple and exploit the ancient artifacts it protects. The players must choose between solving the temple's puzzles, satisfying the ghost's demands, and stopping the rival faction from achieving their goal."

    intro = "Deep beneath the ocean's surface, the players wake up in a flooded temple, their memories foggy and their gear missing. They're forced to rely on their wits, as they explore the temple's damp halls and chambers, fighting off the temple's guardians and searching for a way out"

    adventure = create_summary()
    intro = separate_summary(adventure)

    read_out(intro)

    conversation = [{'role': 'system', 
                     'content': 'You are a fine tuned general language model that follows the prompt exactly.'},
                    {'role': 'assistant', 
                     'content': adventure}]

    goal = create_goal(adventure)
    

    round = 1
    running = True
    while running:
        response = get_next_step(conversation, goal)
        description = response['next_step']
        choice = ask(response['options'])

        skill_level = choice.split(" - ")[0]
        num1, num2 = random.randint(1, 6), random.randint(1, 6)
        read_out(description)
        print(print_dice([num1, num2]))

        if num1 + num2 < int(skill_level):
            conversation.append({'role': 'user', 'content': "The user did not succeed in completing the previous action. Please describe how the player failed and change the story accordingly to accomidate the new situation."})
        conversation.append({'role': 'assistant', 'content': description})
        conversation.append({'role': 'user', 'content': choice})
        # if success == False:
        #     conversation.append({'role': 'user', 'content': "The user did not succeed in completing this action."})
        # elif success == True:
        #     character_level += 1
        # print(f'{character_level=}')
        print(".....Generating.....")
        round += 1



# ChatGPT_model = "gpt-4"  
main()