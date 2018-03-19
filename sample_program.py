#!/usr/bin/env python

from enum import Enum
import json
import sys
import os
from os.path import join
import re
from bs4 import BeautifulSoup
from ricecooker.chefs import SushiChef
from ricecooker.classes import nodes, questions, files
from ricecooker.classes.licenses import get_license
from ricecooker.exceptions import UnknownContentKindError, UnknownFileTypeError, UnknownQuestionTypeError, raise_for_invalid_channel
from le_utils.constants import content_kinds,file_formats, format_presets, licenses, exercises, languages
from pressurecooker.encodings import get_base64_encoding


# CHANNEL SETTINGS
SOURCE_DOMAIN = "source.org"                 # content provider's domain
SOURCE_ID = "Sample Bodhaguru"                             # an alphanumeric channel ID
CHANNEL_TITLE = "Bodhaguru1"       # a humand-readbale title
CHANNEL_LANGUAGE = "en"                            # language code of channel

path_of_xml = "/home/kolibri/Documents/Bodhaguru/xml/"

# LOCAL DIRS
EXAMPLES_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(EXAMPLES_DIR, 'data')
CONTENT_DIR = os.path.join(EXAMPLES_DIR, 'content')
#
# A utility function to manage absolute paths that allows us to refer to files
# in the CONTENT_DIR (subdirectory `content/' in current directory) using content://
def get_abspath(path, content_dir=CONTENT_DIR):
    """
    Replaces `content://` with absolute path of `content_dir`.
    By default looks for content in subdirectory `content` in current directory.
    """
    if path:
        file = re.search('content://(.+)', path)
        if file:
            return os.path.join(content_dir, file.group(1))
    return path



class FileTypes(Enum):
    """ Enum containing all file types Ricecooker can have

        Steps:
            AUDIO_FILE: mp3 files
            THUMBNAIL: png, jpg, or jpeg files
            DOCUMENT_FILE: pdf files
    """
    AUDIO_FILE = 0
    THUMBNAIL = 1
    DOCUMENT_FILE = 2
    VIDEO_FILE = 3
    YOUTUBE_VIDEO_FILE = 4
    VECTORIZED_VIDEO_FILE = 5
    VIDEO_THUMBNAIL = 6
    YOUTUBE_VIDEO_THUMBNAIL_FILE = 7
    HTML_ZIP_FILE = 8
    SUBTITLE_FILE = 9
    TILED_THUMBNAIL_FILE = 10
    UNIVERSAL_SUBS_SUBTITLE_FILE = 11
    BASE64_FILE = 12
    WEB_VIDEO_FILE = 13

kind ={
        "MultipleChoiceSingleAnswer":"single_selection",
        "TrueFalse":"single_selection",
        "MultipleChoiceMultipleAnswer":"multiple_selection",
        "MultipleChoiceDropdown":"single_selection"}
SAMPLE_TREE = {
			"title": "Bodhaguru",
        	"id": "d98752",
        	"description": "v1",
            "children":[]
        }
# count = 1
# final_list = []
# # traverse root directory, and list directories as dirs and files as files
# for directory in os.walk(path_of_xml):
#     temp = directory
#     break

# question_list = []

# for directory in temp[1]:
#     #print(directory)
#     final_dict = {}
#     path_of = path_of_xml+directory+"/"
#     final_dict['title'] = directory
#     final_dict['id'] = directory
#     final_dict['description'] = "v1"
#     final_dict['children'] = []
#     level_files = ["quiz_easy","quiz_hard","quiz_medium"]


#     for level in level_files:
#         #print("In Level")
#         path_to_xml_dict = path_of + level + "/"
#         level_dict = {}
#         level_dict['title'] = level
#         level_dict['id'] = path_to_xml_dict
#         level_dict['description'] = "v1"
#         level_dict['license'] = "All Rights Reserved"
#         level_dict['copyright_holder'] = "Bodhaguru"
#         level_dict['mastery_model'] = exercises.DO_ALL
#         level_dict['questions'] = []
#         for filename in os.listdir(path_to_xml_dict):
#             if filename.endswith(".xml"):
#                 print(filename)
#                 #print("before")
#                 with open(path_to_xml_dict+filename) as file:
#                         xml = BeautifulSoup(file)
#                 #print("After")
#                 children = xml.find_all('queans')
#                 kind1 = kind.keys()
#                 for child in children:
#                     typeof = child.get('type')
#                     if typeof in kind1:
#                         question_dict = {}
#                         question_dict['type'] = kind[child.get('type')]
#                         question_dict['id'] = str(count)
#                         question_dict['question'] = ""
#                         #print("In question")
#                         if child.question.get('text'):
#                             question_dict['question'] = child.question.get('text')
#                         if child.question.get('image'):
#                             question_dict['question'] = question_dict['question'] + " ![]("+path_of_xml+child.question.get('image')+")"
#                         if child.answer.get('feedback'):
#                             question_dict['hints'] = child.answer.get('feedback')

#                         question_dict['all_answers'] = []
#                         if typeof in ["TrueFalse","MultipleChoiceSingleAnswer"]:
#                             options = child.find_all('option')
#                             #print(question_dict['question'])
#                             for opt in options:
#                                 option = ""
#                                 if opt.get('text'):
#                                         option = option + opt.get('text')
#                                 if opt.get('image'):
#                                         option = option + " ![](" +path_of_xml+opt.get('image')+")"
#                                 question_dict['all_answers'].append(option)

#                                 correct = ""
#                                 if len(child.answer.get('correct')) == 1:
#                                     index = int(child.answer.get('correct'))-1
#                                     if options[index].get('text'):
#                                         correct = correct + options[index].get('text')
#                                     if options[index].get('image'):
#                                         correct = correct +  " ![](" +path_of_xml+options[index].get('image') + ")"
#                                 else:
#                                     correct = child.answer.get('correct')
#                             question_dict['correct_answer'] = correct
#                             count = count + 1
#                             #print(question_dict)
#                             level_dict['questions'].append(question_dict)
#                         elif typeof in ["MultipleChoiceMultipleAnswer"]:
#                             options = child.find_all('option')
#                             #print(question_dict['question'])
#                             correct = []
#                             for opt in options:
#                                 option = ""
#                                 if opt.get('text'):
#                                         option = option + opt.get('text')
#                                 if opt.get('image'):
#                                         option = option + " ![](" +path_of_xml+opt.get('image')+")"
#                                 question_dict['all_answers'].append(option)


#                                 if opt.get('correct'):
#                                     correct_ans = ""
#                                     if opt.get('text'):
#                                             correct_ans = correct_ans + opt.get('text')
#                                     if opt.get('image'):
#                                             correct_ans = correct_ans + " ![](" +path_of_xml+opt.get('image')+")"
#                                     correct.append(correct_ans)
#                             question_dict['correct_answers'] = correct
#                             count = count + 1
#                             #print(question_dict)
#                             level_dict['questions'].append(question_dict)
#                         elif typeof in ['MultipleChoiceDropdown']:
#                         	question_dict['question'] = "\n \n"
                        	
#                         	if child.answer.ques.get('text'):
#                         		question_dict['question'] = child.answer.ques.get('text')
#                         	if child.answer.ques.get('image'):
#                         		question_dict['question'] = question_dict['question'] + " ![]("+path_of_xml+child.answer.ques.get('image')+")"
                        	
#                         	options = child.answer.optionbox.find_all('option')
#                         	for opt in options:
#                         		option = ""
#                         		if opt.get('text'):
#                         			option = option + opt.get('text')
#                         		if opt.get('image'):
#                         			option = option + " ![](" +path_of_xml+opt.get('image')+")"
#                         		question_dict['all_answers'].append(option)
#                         	question_dict['correct_answer'] = child.answer.optionbox.get('correct')
#                         	count = count + 1
#                         	level_dict['questions'].append(question_dict)

#             print("************")
#             #print(type(level_dict['questions']))
#             #print("Level dict:::", level_dict)
#         final_dict['children'].append(level_dict)
#     #print("final dict:::", final_dict)
#     SAMPLE_TREE['children'].append(final_dict)


# print(SAMPLE_TREE)



FILE_TYPE_MAPPING = {
    content_kinds.AUDIO : {
        file_formats.MP3 : FileTypes.AUDIO_FILE,
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
    content_kinds.DOCUMENT : {
        file_formats.PDF : FileTypes.DOCUMENT_FILE,
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
    content_kinds.HTML5 : {
        file_formats.HTML5 : FileTypes.HTML_ZIP_FILE,
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
    content_kinds.VIDEO : {
        file_formats.MP4 : FileTypes.VIDEO_FILE,
        file_formats.VTT : FileTypes.SUBTITLE_FILE,
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
    content_kinds.EXERCISE : {
        file_formats.PNG : FileTypes.THUMBNAIL,
        file_formats.JPG : FileTypes.THUMBNAIL,
        file_formats.JPEG : FileTypes.THUMBNAIL,
    },
}



def guess_file_type(kind, filepath=None, youtube_id=None, web_url=None, encoding=None):
    """ guess_file_class: determines what file the content is
        Args:
            filepath (str): filepath of file to check
        Returns: string indicating file's class
    """
    if youtube_id:
        return FileTypes.YOUTUBE_VIDEO_FILE
    elif web_url:
        return FileTypes.WEB_VIDEO_FILE
    elif encoding:
        return FileTypes.BASE64_FILE
    else:
        ext = os.path.splitext(filepath)[1][1:].lower()
        if kind in FILE_TYPE_MAPPING and ext in FILE_TYPE_MAPPING[kind]:
            return FILE_TYPE_MAPPING[kind][ext]
    return None

def guess_content_kind(path=None, web_video_data=None, questions=None):
    """ guess_content_kind: determines what kind the content is
        Args:
            files (str or list): files associated with content
        Returns: string indicating node's kind
    """
    # If there are any questions, return exercise
    if questions and len(questions) > 0:
        return content_kinds.EXERCISE

    # See if any files match a content kind
    if path:
        ext = os.path.splitext(path)[1][1:].lower()
        if ext in content_kinds.MAPPING:
            return content_kinds.MAPPING[ext]
        raise InvalidFormatException("Invalid file type: Allowed formats are {0}".format([key for key, value in content_kinds.MAPPING.items()]))
    elif web_video_data:
        return content_kinds.VIDEO
    else:
        return content_kinds.TOPIC








SAMPLE_TREE = [{'id': 'd98752', 'title': 'Bodhaguru', 'children': [{'id': 'animal_homes', 'title': 'animal_homes', 'children': [{'id': '/home/kolibri/Documents/Bodhaguru/xml/animal_homes/quiz_easy/', 'license': 'All Rights Reserved', 'copyright_holder': 'Bodhaguru', 'description': 'v1', 'questions': [{'id': '1', 'hints': "Fox don't live in farm", 'type': 'single_selection', 'all_answers': ['Horse', 'Goat', 'Fox'], 'correct_answer': 'Fox', 'question': 'Which is not a farm animal?'}, {'id': '2', 'hints': 'A frog can live in water, also lives on land', 'type': 'single_selection', 'all_answers': ['Frog', 'Dog', 'Rabbit'], 'correct_answer': 'Frog', 'question': 'Which animal can live both in water and on land?'}, {'id': '3', 'hints': 'Wild animals live in jungle like tiger', 'type': 'single_selection', 'all_answers': ['Farm animal', 'Wild animal', 'Domestic animal'], 'correct_answer': 'Wild animal', 'question': 'An animal which lives in jungle is called a ____'}, {'id': '4', 'hints': "Cheetah is very ferocious so can't be farm animal", 'type': 'single_selection', 'all_answers': ['Yes', 'No'], 'correct_answer': 'No', 'question': 'Can cheetah be a farm animal?'}, {'id': '5', 'hints': 'Shark is sea animal', 'type': 'single_selection', 'all_answers': ['Bear', 'Shark', 'Tiger'], 'correct_answer': 'Shark', 'question': 'Which animal lives in sea?'}, {'id': '6', 'hints': 'Tiger lives in den', 'type': 'single_selection', 'all_answers': ['Pigeon', 'Bee', 'Tiger'], 'correct_answer': 'Tiger', 'question': 'Can you tell which of the following animals live in a natural home?'}, {'id': '7', 'type': 'single_selection', 'correct_answer': 'Stable', 'all_answers': ['Pen', 'Burrow', 'Stable'], 'question': 'Where does horse live?'}, {'id': '8', 'hints': 'We make homes for animals like cow, goat, horse etc.', 'type': 'multiple_selection', 'all_answers': ['Wild animals', 'Farm animals', 'Domestic animals'], 'correct_answers': ['Farm animals', 'Domestic animals'], 'question': 'Humans make home for ____'}], 'title': 'quiz_easy', 'mastery_model': 'do_all'}, {'id': '/home/kolibri/Documents/Bodhaguru/xml/animal_homes/quiz_hard/', 'license': 'All Rights Reserved', 'copyright_holder': 'Bodhaguru', 'description': 'v1', 'questions': [{'id': '9', 'hints': 'Bear lives in cave called its den.', 'type': 'single_selection', 'all_answers': ['Den', 'Burrow', 'Coop'], 'correct_answer': 'Den', 'question': 'Where does bear live?'}, {'id': '10', 'hints': 'Many people make rabbit pet as it is harmless', 'type': 'single_selection', 'all_answers': ['Wolf', 'Rabbit', 'Bee'], 'correct_answer': 'Rabbit', 'question': 'Which wild animal can be a pet too?'}, {'id': '11', 'hints': "Many animals that don't make home stay in group or protect themselves in many other ways", 'type': 'multiple_selection', 'all_answers': ['They are too lazy', 'They stay in group', 'They have other way to stay safe'], 'correct_answers': ['They stay in group', 'They have other way to stay safe'], 'question': "Why don't certain animals make home?"}, {'id': '12', 'hints': 'Snake and mouse both live in hole', 'type': 'multiple_selection', 'all_answers': ['Snake', 'Mouse', 'Cat'], 'correct_answers': ['Snake', 'Mouse'], 'question': 'Which all animals live in a hole?'}, {'id': '13', 'hints': 'Lion lives in cave', 'type': 'single_selection', 'all_answers': [' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/lion.png)', ' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/goat.png)', ' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/bird.png)', ' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/dog.png)'], 'correct_answer': ' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/lion.png)', 'question': "Which one of these animals doesn't make its home but lives in natural home?"}, {'id': '14', 'hints': "Elephants keep wandering and they can protect themselves so they don't make permanent home", 'type': 'multiple_selection', 'all_answers': ['They keep wandering ', 'They can protect themselves', 'They are too lazy'], 'correct_answers': ['They keep wandering ', 'They can protect themselves'], 'question': "Why doesn't elephant make home?"}, {'id': '15', 'hints': 'An animal makes home for same reason like us, for safety and to take rest', 'type': 'single_selection', 'all_answers': ['For luxury only', 'To show others', 'For safety'], 'correct_answer': 'For safety', 'question': 'Why do animals make home?'}, {'id': '16', 'hints': 'They are not domesticated by us.', 'type': 'single_selection', 'all_answers': ['Yes', 'No'], 'correct_answer': 'No', 'question': 'Cockroaches, bugs etc. also live in our homes. Does that mean they are domestic animal?'}, {'id': '17', 'hints': 'We often see sparrow making nest somewhere in our homes', 'type': 'single_selection', 'all_answers': ['Vulture', 'Sparrow', 'Eagle'], 'correct_answer': 'Sparrow', 'question': 'Which bird makes nest in our homes?'}], 'title': 'quiz_hard', 'mastery_model': 'do_all'}, {'id': '/home/kolibri/Documents/Bodhaguru/xml/animal_homes/quiz_medium/', 'license': 'All Rights Reserved', 'copyright_holder': 'Bodhaguru', 'description': 'v1', 'questions': [{'id': '18', 'type': 'single_selection', 'correct_answer': ' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/lion.png)', 'all_answers': [' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/goat.png)', ' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/lion.png)', ' ![](/home/kolibri/Documents/Bodhaguru/xml/animal_homes/dog.png)'], 'question': "Which animal can't live with us?"}, {'id': '19', 'type': 'single_selection', 'correct_answer': 'Kennel', 'all_answers': ['Stable', 'Shed', 'Kennel'], 'question': 'What is the home of dog called?'}, {'id': '20', 'hints': "Lion lives in natural home, elephant doesn't make home", 'type': 'single_selection', 'all_answers': ['They keep roaming', 'They live in natural home', 'Either A or B'], 'correct_answer': 'Either A or B', 'question': 'Some animals do not make homes. So ___'}, {'id': '21', 'type': 'single_selection', 'correct_answer': 'cow-shed', 'all_answers': ['cow-shed', 'barrack', 'pen'], 'question': 'Cow lives in ____ '}, {'id': '22', 'hints': 'Zebra doesn’t make home. They live in group and keep wandering', 'type': 'single_selection', 'all_answers': ['Fox', 'Zebra', 'Lion'], 'correct_answer': 'Zebra', 'question': 'Which of these animals never makes any home?'}, {'id': '23', 'hints': 'Hens live in coop', 'type': 'single_selection', 'all_answers': ['Pen', 'Coop', 'Shed'], 'correct_answer': 'Coop', 'question': 'Where do hens stay in poultry?'}, {'id': '24', 'hints': 'Birds make nest on tree', 'type': 'single_selection', 'all_answers': ['Rabbit', 'Snake', 'Bird'], 'correct_answer': 'Bird', 'question': 'Which animal makes its home on tree?'}, {'id': '25', 'hints': 'Wolf is ferocious, so people don’t try to make it a pet', 'type': 'single_selection', 'all_answers': ['It is harmless', 'It is ferocious', 'It can’t be captured'], 'correct_answer': 'It is ferocious', 'question': 'Why people never try to make a wolf their pet?'}], 'title': 'quiz_medium', 'mastery_model': 'do_all'}], 'description': 'v1'}, {'id': 'plant_parts', 'title': 'plant_parts', 'children': [{'id': '/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_easy/', 'license': 'All Rights Reserved', 'copyright_holder': 'Bodhaguru', 'description': 'v1', 'questions': [{'id': '26', 'hints': 'Carrot itself is the main root of carrot plant', 'type': 'single_selection', 'all_answers': ['Tap root', 'Fibrous root', 'Respiratory root'], 'correct_answer': 'Tap root', 'question': 'Carrot is actually an example of _____ root.'}, {'id': '27', 'type': 'single_selection', 'correct_answer': 'Watermelon', 'all_answers': ['Lemon', 'Watermelon', 'Mango'], 'question': 'Which fruit has highest number of seeds among the given option?'}, {'id': '28', 'type': 'single_selection', 'correct_answer': 'Banana', 'all_answers': ['Banana', 'Litchi', 'Orange'], 'question': 'A seedless fruit is ____'}, {'id': '29', 'hints': 'Leaves needs sunlight to make food', 'type': 'single_selection', 'all_answers': ['Light makes shoot colourful ', 'Leaf needs sunlight to make food ', 'To protect itself from insects'], 'correct_answer': 'Leaf needs sunlight to make food ', 'question': 'What is the main reason for the shoot to grow above the ground? '}, {'id': '30', 'hints': 'Leaves grow on branches which is part of shoot', 'type': 'single_selection', 'all_answers': ['True', 'False'], 'correct_answer': 'False', 'question': 'Leaves are part of root.'}, {'id': '31', 'type': 'single_selection', 'correct_answer': 'It absorbs water from soil', 'all_answers': ['It absorbs water from soil', 'It grows fruit', 'It prepares food'], 'question': 'What is the function of root?'}, {'id': '32', 'type': 'single_selection', 'correct_answer': 'Root and shoot', 'all_answers': ['Shoot and branches', 'Root and shoot', 'Root and branches'], 'question': 'Two major parts of trees are ____'}], 'title': 'quiz_easy', 'mastery_model': 'do_all'}, {'id': '/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_hard/', 'license': 'All Rights Reserved', 'copyright_holder': 'Bodhaguru', 'description': 'v1', 'questions': [{'id': '33', 'hints': 'Radish is a root', 'type': 'single_selection', 'all_answers': ['Cabbage', 'Spinach', 'Radish'], 'correct_answer': 'Radish', 'question': 'Which vegetable is not a part of shoot?'}, {'id': '34', 'hints': 'In fibrous root all the roots look same as there is no main root', 'type': 'single_selection', 'all_answers': ['Tap root', 'Fibrous root', 'Respiratory root'], 'correct_answer': 'Fibrous root', 'question': 'All the roots of paddy plant are almost same, no root is much thicker or longer than the others. So it has ___'}, {'id': '35', 'hints': 'It has main root', 'type': 'single_selection', 'all_answers': ['Tap root', 'Fibrous root'], 'correct_answer': 'Tap root', 'question': 'What kind of root is this? ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_hard/plant.png)'}, {'id': '36', 'hints': 'Plant cannot survive with damaged root.', 'type': 'single_selection', 'all_answers': ['Its root was damaged', 'Few leaves were damaged', 'One branch was broken'], 'correct_answer': 'Its root was damaged', 'question': "A boy uprooted a plant by mistake and then planted it back. But it didn't grow. Why?"}], 'title': 'quiz_hard', 'mastery_model': 'do_all'}, {'id': '/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/', 'license': 'All Rights Reserved', 'copyright_holder': 'Bodhaguru', 'description': 'v1', 'questions': [{'id': '37', 'hints': 'Thorns on the stem prick anyone who approaches the rose plant to pluck its flower', 'type': 'single_selection', 'all_answers': [' ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/root.png)', ' ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/throns.png)', ' ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/bud1.png)', ' ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/leaf.png)'], 'correct_answer': ' ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/throns.png)', 'question': 'What part helps rose on the plant to safe guard itself'}, {'id': '38', 'hints': 'Root absorbs water from soil', 'type': 'single_selection', 'all_answers': ['To prepare food', 'To grow fruit', 'To absorb water'], 'correct_answer': 'To absorb water', 'question': 'Why does root grow underground?'}, {'id': '39', 'hints': 'Shoot is made of stem and branches', 'type': 'single_selection', 'all_answers': ['Shoot ', 'Root', 'Branches'], 'correct_answer': 'Shoot ', 'question': 'Stem is a part of ____'}, {'id': '40', 'hints': 'Grass has fibrous root', 'type': 'single_selection', 'all_answers': ['True', 'False'], 'correct_answer': 'False', 'question': 'Grass has tap root.'}, {'id': '41', 'hints': 'Leaf prepares food', 'type': 'single_selection', 'all_answers': ['Leaf ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/leaf1.png)', 'Stem ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/stem.png)', 'Fruit ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/fruit1.png)'], 'correct_answer': 'Leaf ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_medium/leaf1.png)', 'question': 'I am a flat and green part of the plant that cooks food for the whole plant. Can you guess who I am?'}, {'id': '42', 'hints': 'Food travels to the other parts of plant through the stem', 'type': 'single_selection', 'all_answers': ['Through root', 'Through stem', 'Through air'], 'correct_answer': 'Through stem', 'question': 'How does food from leaf reach other parts of plant?'}, {'id': '43', 'hints': 'Plants need sunlight to prepare food', 'type': 'single_selection', 'all_answers': ['Plant gets scared', 'Because of lack of air', 'Because of no sunlight'], 'correct_answer': 'Because of no sunlight', 'question': "Why can't plant grow in dark room?"}, {'id': '44', 'hints': 'Water is necessary for plants to grow', 'type': 'single_selection', 'all_answers': ["Plants don't like sunlight", 'Water scarcity', 'Violent wind uproots plants'], 'correct_answer': 'Water scarcity', 'question': 'Why do deserts have very few or no trees?'}, {'id': '45', 'hints': 'Main root is present in tap root', 'type': 'single_selection', 'all_answers': ['Fibrous root ', 'Tap root', 'Both tap and fibrous root'], 'correct_answer': 'Tap root', 'question': 'Main root is present in _____'}], 'title': 'quiz_medium', 'mastery_model': 'do_all'}], 'description': 'v1'}], 'description': 'v1'}]



# SAMPLE_TREE = [
# 		{
# 			"title": "Bodhaguru",
#         	"id": "d98752",
#         	"description": "Start cooking rice today!",
#         	"children": [
#         	{
#                 "title": "Rice Exercise",
#                 "id": "6cafe3",
#                 "description": "Test how well you know your rice",
#                 "license": "CC BY",
#                 "copyright_holder": "Learning Equality",
#                 "mastery_model": exercises.DO_ALL,
#                 "files": [
#                     {
#                         "path": "http://www.publicdomainpictures.net/pictures/110000/nahled/bowl-of-rice.jpg",
#                     }
#                 ],
#                 "questions": [
#                     {
#                         "id": "bbbbb",
#                         "question": "What kind of root is this? ![](/home/kolibri/Documents/Bodhaguru/xml/plant_parts/quiz_hard/plant.png)",
#                         "type":"single_selection",
#                         "correct_answer": "Tap root",
#                         "all_answers": [
#                             "Tap root",
#                             "Fibrous root",
#                         ],
#                         "hints": "It has main root",
#                     }]
# 		}]
# 	}]
#
#


class SampleChef(SushiChef):
    """
    The chef class that takes care of uploading channel to the content curation server.

    We'll call its `main()` method from the command line script.
    """
    channel_info = {    #
        'CHANNEL_SOURCE_DOMAIN': SOURCE_DOMAIN,       # who is providing the content (e.g. learningequality.org)
        'CHANNEL_SOURCE_ID': SOURCE_ID,                   # channel's unique id
        'CHANNEL_TITLE': CHANNEL_TITLE,
        'CHANNEL_LANGUAGE': CHANNEL_LANGUAGE,
        #'CHANNEL_THUMBNAIL': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Banaue_Philippines_Banaue-Rice-Terraces-01.jpg/640px-Banaue_Philippines_Banaue-Rice-Terraces-01.jpg', # (optional) local path or url to image file
        #'CHANNEL_DESCRIPTION': 'A sample sushi chef to demo content types.',      # (optional) description of the channel (optional)
    }

    def construct_channel(self, *args, **kwargs):
        """
        Create ChannelNode and build topic tree.
        """
        channel = self.get_channel(*args, **kwargs)   # creates ChannelNode from data in self.channel_info
        _build_tree(channel, SAMPLE_TREE)
        raise_for_invalid_channel(channel)

        return channel


def _build_tree(node, sourcetree):
    """
    Parse nodes given in `sourcetree` and add as children of `node`.
    """
    for child_source_node in sourcetree:
        try:
            main_file = child_source_node['files'][0] if 'files' in child_source_node else {}
            kind = guess_content_kind(path=main_file.get('path') or main_file.get('web_url'), questions=child_source_node.get("questions"))
        except UnknownContentKindError:
            continue

        if kind == content_kinds.TOPIC:
            child_node = nodes.TopicNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                author=child_source_node.get("author"),
                description=child_source_node.get("description"),
                thumbnail=child_source_node.get("thumbnail"),
            )
            node.add_child(child_node)

            source_tree_children = child_source_node.get("children", [])

            _build_tree(child_node, source_tree_children)

        elif kind == content_kinds.VIDEO:
            child_node = nodes.VideoNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                license=get_license(child_source_node.get("license"), description="Description of license", copyright_holder=child_source_node.get('copyright_holder')),
                author=child_source_node.get("author"),
                description=child_source_node.get("description"),
                derive_thumbnail=True, # video-specific data
                thumbnail=child_source_node.get('thumbnail'),
            )
            add_files(child_node, child_source_node.get("files") or [])
            node.add_child(child_node)

        elif kind == content_kinds.AUDIO:
            child_node = nodes.AudioNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                license=child_source_node.get("license"),
                author=child_source_node.get("author"),
                description=child_source_node.get("description"),
                thumbnail=child_source_node.get("thumbnail"),
                copyright_holder=child_source_node.get("copyright_holder"),
            )
            add_files(child_node, child_source_node.get("files") or [])
            node.add_child(child_node)

        elif kind == content_kinds.DOCUMENT:
            child_node = nodes.DocumentNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                license=child_source_node.get("license"),
                author=child_source_node.get("author"),
                description=child_source_node.get("description"),
                thumbnail=child_source_node.get("thumbnail"),
                copyright_holder=child_source_node.get("copyright_holder"),
            )
            add_files(child_node, child_source_node.get("files") or [])
            node.add_child(child_node)

        elif kind == content_kinds.EXERCISE:
            mastery_model = (child_source_node.get('mastery_model') and {"mastery_model": child_source_node['mastery_model']}) or {}
            child_node = nodes.ExerciseNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                license=child_source_node.get("license"),
                author=child_source_node.get("author"),
                description=child_source_node.get("description"),
                exercise_data=mastery_model,
                thumbnail=child_source_node.get("thumbnail"),
                copyright_holder=child_source_node.get("copyright_holder"),
            )
            add_files(child_node, child_source_node.get("files") or [])
            for q in child_source_node.get("questions"):
                question = create_question(q)
                child_node.add_question(question)
            node.add_child(child_node)

        elif kind == content_kinds.HTML5:
            child_node = nodes.HTML5AppNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                license=child_source_node.get("license"),
                author=child_source_node.get("author"),
                description=child_source_node.get("description"),
                thumbnail=child_source_node.get("thumbnail"),
                copyright_holder=child_source_node.get("copyright_holder"),
            )
            add_files(child_node, child_source_node.get("files") or [])
            node.add_child(child_node)

        else:                   # unknown content file format
            continue

    return node

def add_files(node, file_list):
    for f in file_list:

        path = f.get('path')
        if path is not None:
            abspath = get_abspath(path)      # NEW: expand  content://  -->  ./content/  in file paths
        else:
            abspath = None

        file_type = guess_file_type(node.kind, filepath=abspath, youtube_id=f.get('youtube_id'), web_url=f.get('web_url'), encoding=f.get('encoding'))

        if file_type == FileTypes.AUDIO_FILE:
            node.add_file(files.AudioFile(path=abspath, language=f.get('language')))
        elif file_type == FileTypes.THUMBNAIL:
            node.add_file(files.ThumbnailFile(path=abspath))
        elif file_type == FileTypes.DOCUMENT_FILE:
            node.add_file(files.DocumentFile(path=abspath, language=f.get('language')))
        elif file_type == FileTypes.HTML_ZIP_FILE:
            node.add_file(files.HTMLZipFile(path=abspath, language=f.get('language')))
        elif file_type == FileTypes.VIDEO_FILE:
            node.add_file(files.VideoFile(path=abspath, language=f.get('language'), ffmpeg_settings=f.get('ffmpeg_settings')))
        elif file_type == FileTypes.SUBTITLE_FILE:
            node.add_file(files.SubtitleFile(path=abspath, language=f['language']))
        elif file_type == FileTypes.BASE64_FILE:
            node.add_file(files.Base64ImageFile(encoding=f['encoding']))
        elif file_type == FileTypes.WEB_VIDEO_FILE:
            node.add_file(files.WebVideoFile(web_url=f['web_url'], high_resolution=f.get('high_resolution')))
        elif file_type == FileTypes.YOUTUBE_VIDEO_FILE:
            node.add_file(files.YouTubeVideoFile(youtube_id=f['youtube_id'], high_resolution=f.get('high_resolution')))
            node.add_file(files.YouTubeSubtitleFile(youtube_id=f['youtube_id'], language='en'))
        else:
            raise UnknownFileTypeError("Unrecognized file type '{0}'".format(f['path']))

def create_question(raw_question):
    question = parse_images(raw_question.get('question'))
    hints = raw_question.get('hints')
    hints = parse_images(hints) if isinstance(hints, str) else [parse_images(hint) for hint in hints or []]

    if raw_question["type"] == exercises.MULTIPLE_SELECTION:
        return questions.MultipleSelectQuestion(
            id=raw_question["id"],
            question=question,
            correct_answers=[parse_images(answer) for answer in raw_question['correct_answers']],
            all_answers=[parse_images(answer) for answer in raw_question['all_answers']],
            hints=hints,
        )
    if raw_question["type"] == exercises.SINGLE_SELECTION:
        return questions.SingleSelectQuestion(
            id=raw_question["id"],
            question=question,
            correct_answer=parse_images(raw_question['correct_answer']),
            all_answers=[parse_images(answer) for answer in raw_question['all_answers']],
            hints=hints,
        )
    if raw_question["type"] == exercises.INPUT_QUESTION:
        return questions.InputQuestion(
            id=raw_question["id"],
            question=question,
            answers=[parse_images(answer) for answer in raw_question['answers']],
            hints=hints,
        )
    if raw_question["type"] == exercises.PERSEUS_QUESTION:
        return questions.PerseusQuestion(
            id=raw_question["id"],
            raw_data=parse_images(raw_question.get('item_data')),
            source_url="https://www.google.com/",
        )
    else:
        raise UnknownQuestionTypeError("Unrecognized question type '{0}': accepted types are {1}".format(raw_question["type"], [key for key, value in exercises.question_choices]))

def parse_images(content):
    if content:
        reg = re.compile(questions.FILE_REGEX, flags=re.IGNORECASE)
        matches = reg.findall(content)
        for match in matches:
            path = match[1]
            graphie = re.search(questions.WEB_GRAPHIE_URL_REGEX, path)
            if graphie:
                path = graphie.group(1)
            content = content.replace(path, get_abspath(path).replace('\\', '\\\\'))
    return content



if __name__ == '__main__':
    """
    This code will run when the sushi chef is called from the command line.
    """

    chef = SampleChef()
    chef.main()
