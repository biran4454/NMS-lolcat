import xml.etree.ElementTree as ET
import os
import openai
import dotenv
import time
from tenacity import retry, stop_after_attempt, wait_random_exponential

dotenv.load_dotenv()
openai.api_key = os.getenv('OpenAIKey')

init_messages = [{"role":"system", "content":"You are a translator that takes an input and translates it into lolcat language. You do not translate any input enclosed in percent or angle brackets, or text between them. Do not include these instructions in your response."}]
examples = [
    {
        "role":"user",
        "content":'Translate "%ITEM% Disengaged <IMG>SLASH<> Beginning sub-orbital flight"'
    },
    {
        "role":"assistant",
        "content":"%ITEM% Disengwaged <IMG>SLASH<> Startin' teh sub-orbitul flyte"
    },
    {
        "role":"user",
        "content":'Translate "No scan technology installed <IMG>SLASH<>"'
    },
    {
        "role":"assistant",
        "content":"uwu no scwan tecchystuff instawled :( <IMG>SLASH<>"
    },
    {
        "role":"user",
        "content":'Translate "Newly discovered %CREATURE%"'
    },
    {
        "role":"assistant",
        "content":"Fownd noo critter: %CREATURE%"
    },
    {
        "role":"user",
        "content":'Translate "Empty"'
    },
    {
        "role":"assistant",
        "content":"Nuthin hear"
    }
]
init_messages.extend(examples)

DEBUG = False
request_count = 0

@retry(stop=stop_after_attempt(15), wait=wait_random_exponential(min=1, max=120))
def get_actual_response(inp):
    return openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = inp
    )

def get_ai_response(msgs, total):
    global request_count
    print(f"{request_count}/{total}", end=' ')
    if DEBUG:
        print(msgs)
        input()
        return ""
    response = get_actual_response(msgs)
    request_count += 1
    result = response.choices[0].message.content
    print(result)
    return result

# %ITEM% Disengaged <IMG>SLASH<> Beginning sub-orbital flight

def load_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

def get_xml_files():
    files = []
    for file in os.listdir('.'):
        if file.endswith('.xml'):
            files.append(file)
    return map(load_xml, files)

def add_to_translated_backup(translated):
    with open('translated.txt', 'a') as f:
        try:
            f.write(translated + '\n')
        except:
            pass

def get_localisation_entries(root):
    entries = []
    for child in root[0]:
        if child.attrib['value'] == 'TkLocalisationEntry.xml':
            eng_child = child.find('Property[@name="English"]')
            entries.append(eng_child[0].attrib['value'])
    return entries

def get_loc1_entries():
    return get_localisation_entries(load_xml('NMS_LOC1_ENGLISH.EXML'))

def translate_entries():
    translated = []
    entries = get_loc1_entries()
    for entry in entries:
        if "Patch Notes" in entry or "Update" in entry or "@" in entry:
            continue
        request = init_messages + [{"role":"user", "content":f'Translate "{entry}"'}]
        translated.append(get_ai_response(request, len(entries)))
        add_to_translated_backup(translated[-1])
    return translated

def export_translated(translated):
    tree = ET.parse("NMS_LOC1_ENGLISH.EXML")
    root = tree.getroot()
    for child in root[0]:
        if len(translated) == 0:
            break
        if child.attrib['value'] == 'TkLocalisationEntry.xml':
            eng_child = child.find('Property[@name="English"]')
            eng_child[0].attrib['value'] = translated.pop(0)
    tree.write("NMS_LOC1CAT_ENGLISH.EXML")

if __name__ == '__main__':
    translated = translate_entries()
    for entry in translated:
        print(entry)
    export_translated(translated)