#!/usr/bin/env python

from enum import Enum
import json
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
import zipfile
import shutil # Imported to delete directory
import uuid
import sys
# CHANNEL SETTINGS
SOURCE_DOMAIN = "bodhaguru.com"                 # content provider's domain
SOURCE_ID = "BodhaGuru CBSE Hindi"                             # an alphanumeric channel ID
CHANNEL_TITLE = "BodhaGuru CBSE Hindi"       # a humand-readbale title
CHANNEL_LANGUAGE = "en"                            # language code of channel
CHANNEL_THUMBNAIL = "/home/kolibri/Documents/Bodhaguru/CBSE_Bodhaguru/Hindi_channel/BG.jpg"
count = 1
path_of_content= "/home/kolibri/Documents/Bodhaguru/CBSE_Bodhaguru/content/Hindi/"

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

def getOptionImage(opt, option, path,path_of):
    if os.path.isfile(path+opt.get('image')):
        option = option + " ![](" +path+opt.get('image')+")"
    else:
        option = option + " ![](" +path_of+opt.get('image')+")"
    return option

def mastery_calculation(count):
    M = count - 3
    if count < 4:
            exercise_data = { 'mastery_model': exercises.DO_ALL,
        'randomize': True
        }
    elif count == 5 or count == 4:
        exercise_data = { 'mastery_model': exercises.M_OF_N,
        'randomize': True,
        'm': 3,
        'n': count,
        }
    else:
        exercise_data = { 'mastery_model': exercises.M_OF_N,
        'randomize': True,
        'm': M,
        'n': count,
        }
    return exercise_data

def getCounter():
    return str(uuid.uuid4())

dict_structure1 = ['Class1','Class2','Class3','Class4','Class5','Class6','Class7','Class8','Class9','Class10']
#dict_structure1 = ['Class10']
#dict_structure2 = ['Exercises','Video']
dict_structure2 = ['Video']

def levelDictInitialization():
    level_dict = {}
    level_dict['id'] = str(getCounter())
    level_dict['description'] = "v1"
    level_dict['license'] = "All Rights Reserved"
    level_dict['copyright_holder'] = "BodhaGuru"
    level_dict['questions'] = []
    return level_dict


def foldersCreationInJson(folder):
    folder_dict = {}
    folder_dict['title'] = folder
    folder_dict['id'] = str(getCounter())
    folder_dict['description'] = 'v1'
    folder_dict['children'] = []
    return folder_dict


def sort_folders(list_of_folder):
    list_of_folder.sort(key = lambda x : int(x.split(".")[0]))
    return(list_of_folder)


def video_node(video_path, subfolder_name):
    video_dict = {}
    video_dict['id'] = str(getCounter())
    video_dict['title'] = subfolder_name.replace('_.mp4','')
    video_dict['license'] = "All Rights Reserved"
    video_dict['copyright_holder'] = "BodhaGuru"
    video_dict['files']=[{"path": video_path+subfolder_name}]
    return video_dict


def exercise_scrapping(filename, path):

    final_dict = {}
    path_of = path + filename.replace('.zip','') + '/'
    final_dict['title'] = filename.replace('.zip','')
    final_dict['id'] = str(getCounter())
    final_dict['description'] = "v1"
    final_dict['children'] = []
    for  root, dirs, temp_files  in os.walk(path_of):
        if len(dirs) == 0:
            for xml_file in temp_files:
                if xml_file.endswith('.xml'):
                    level_dict = levelDictInitialization()
                    level_dict['title'] = xml_file.replace('.xml', '')
                    print("Name of xml:::***********",xml_file )

                    with open(path_of+xml_file) as file:
                        xml = BeautifulSoup(file)
                    children = xml.find_all('queans')
                    kind1 = kind.keys()
                    for child in children:
                        typeof = child.get('type')
                        if typeof in kind1:
                            question_dict = {}
                            question_dict['type'] = kind[child.get('type')]
                            question_dict['id'] = str(getCounter())
                            question_dict['question'] = ""
                            if child.question.get('text'):
                                question_dict['question'] = child.question.get('text')
                            if child.question.get('image'):
                                if os.path.isfile(path+child.question.get('image')):
                                    question_dict['question'] = question_dict['question'] + " ![]("+path+child.question.get('image')+")"
                                else:
                                    question_dict['question'] = question_dict['question'] + " ![]("+path_of+child.question.get('image')+")"

                            if child.answer.get('feedback'):
                                question_dict['hints'] = child.answer.get('feedback')

                            question_dict['all_answers'] = []
                            if typeof in ["TrueFalse","MultipleChoiceSingleAnswer"]:
                                options = child.find_all('option')
                                for opt in options:
                                    option = ""
                                    if opt.get('text'):
                                        option = option + opt.get('text')
                                    if opt.get('image'):
                                        option = getOptionImage(opt, option ,path, path_of)

                                    question_dict['all_answers'].append(option)

                                    correct = ""
                                    if len(child.answer.get('correct')) == 1:
                                        index = int(child.answer.get('correct'))-1

                                        if options[index].get('text'):
                                            correct = correct + options[index].get('text')
                                        if options[index].get('image'):
                                            if os.path.isfile(path+options[index].get('image')):
                                                correct = correct +  " ![](" +path+options[index].get('image') + ")"
                                            else:
                                                correct = correct +  " ![](" +path_of+options[index].get('image') + ")"
                                    else:
                                        correct = child.answer.get('correct')
                                question_dict['correct_answer'] = correct
                                level_dict['questions'].append(question_dict)
                            elif typeof in ["MultipleChoiceMultipleAnswer"]:
                                options = child.find_all('option')
                                correct = []
                                for opt in options:
                                    option = ""
                                    if opt.get('text'):
                                            option = option + opt.get('text')
                                    if opt.get('image'):
                                        option = getOptionImage(opt, option ,path, path_of)
                                    question_dict['all_answers'].append(option)


                                    if opt.get('correct'):
                                        correct_ans = ""
                                        if opt.get('text'):
                                                correct_ans = correct_ans + opt.get('text')
                                        if opt.get('image'):
                                            correct_ans = getOptionImage(opt, correct_ans ,path, path_of)
                                        correct.append(correct_ans)
                                question_dict['correct_answers'] = correct
                                level_dict['questions'].append(question_dict)
                            elif typeof in ['MultipleChoiceDropdown']:
                                question_dict['question'] = "\n \n"

                                if child.answer.ques.get('text'):
                                    question_dict['question'] = child.answer.ques.get('text')
                                if child.answer.ques.get('image'):
                                    if os.path.isfile(path+child.answer.ques.get('image')):
                                        question_dict['question'] = question_dict['question'] + " ![]("+path+child.answer.ques.get('image')+")"
                                    else:
                                        question_dict['question'] = question_dict['question'] + " ![]("+path_of+child.answer.ques.get('image')+")"


                                options = child.answer.optionbox.find_all('option')
                                for opt in options:
                                    option = ""
                                    if opt.get('text'):
                                        option = option + opt.get('text')
                                    if opt.get('image'):
                                        option = getOptionImage(opt, option ,path, path_of)

                                    question_dict['all_answers'].append(option)
                                question_dict['correct_answer'] = child.answer.optionbox.get('correct')
                                count = count + 1
                                level_dict['questions'].append(question_dict)

                    final_dict['children'].append(level_dict)

        else:
            level_files = ["quiz_easy","quiz_hard","quiz_medium"]

            for level in level_files:
                path_to_xml_dict = path_of  + level + "/"
                if os.path.isdir(path_to_xml_dict):
                    level_dict = levelDictInitialization()
                    level_dict['title'] = level

                    for filename in os.listdir(path_to_xml_dict):
                        if filename.endswith(".xml"):

                            with open(path_to_xml_dict+filename) as file:
                                    xml = BeautifulSoup(file)

                            children = xml.find_all('queans')
                            kind1 = kind.keys()
                            for child in children:
                                typeof = child.get('type')
                                if typeof in kind1:
                                    question_dict = {}
                                    question_dict['type'] = kind[child.get('type')]
                                    question_dict['id'] = str(getCounter())
                                    question_dict['question'] = ""
                                    if child.question.get('text'):
                                        question_dict['question'] = child.question.get('text')
                                    if child.question.get('image'):
                                        if os.path.isfile(path+child.question.get('image')):
                                            question_dict['question'] = question_dict['question'] + " ![]("+path+child.question.get('image')+")"
                                        else:
                                            question_dict['question'] = question_dict['question'] + " ![]("+path_to_xml_dict+child.question.get('image')+")"
                                    if child.answer.get('feedback'):
                                        question_dict['hints'] = child.answer.get('feedback')

                                    question_dict['all_answers'] = []
                                    if typeof in ["TrueFalse","MultipleChoiceSingleAnswer"]:
                                        options = child.find_all('option')
                                        for opt in options:
                                            option = ""
                                            if opt.get('text'):
                                                    option = option + opt.get('text')
                                            if opt.get('image'):
                                                option = getOptionImage(opt, option, path, path_to_xml_dict)

                                            question_dict['all_answers'].append(option)

                                            correct = ""
                                            if len(child.answer.get('correct')) == 1:
                                                index = int(child.answer.get('correct'))-1
                                                if options[index].get('text'):
                                                    correct = correct + options[index].get('text')
                                                if options[index].get('image'):
                                                    if os.path.isfile(path+options[index].get('image')):
                                                        correct = correct +  " ![](" +path+options[index].get('image') + ")"
                                                    else:
                                                        correct = correct +  " ![](" +path_to_xml_dict+options[index].get('image') + ")"
                                            else:
                                                correct = child.answer.get('correct')
                                        question_dict['correct_answer'] = correct
                                        level_dict['questions'].append(question_dict)
                                    elif typeof in ["MultipleChoiceMultipleAnswer"]:
                                        options = child.find_all('option')
                                        correct = []
                                        for opt in options:
                                            option = ""
                                            if opt.get('text'):
                                                    option = option + opt.get('text')
                                            if opt.get('image'):
                                                option = getOptionImage(opt, option, path, path_to_xml_dict)
                                            question_dict['all_answers'].append(option)


                                            if opt.get('correct'):
                                                correct_ans = ""
                                                if opt.get('text'):
                                                        correct_ans = correct_ans + opt.get('text')
                                                if opt.get('image'):
                                                    correct_ans = option = getOptionImage(opt, correct_ans, path, path_to_xml_dict)
                                                correct.append(correct_ans)
                                        question_dict['correct_answers'] = correct
                                        level_dict['questions'].append(question_dict)
                                    elif typeof in ['MultipleChoiceDropdown']:
                                        question_dict['question'] = "\n \n"

                                        if child.answer.ques.get('text'):
                                            question_dict['question'] = child.answer.ques.get('text')
                                        if child.answer.ques.get('image'):
                                            if os.path.isfile(path+child.answer.ques.get('image')):
                                                question_dict['question'] = question_dict['question'] + " ![]("+path+child.answer.ques.get('image')+")"
                                            else:
                                                question_dict['question'] = question_dict['question'] + " ![]("+path_to_xml_dict+child.answer.ques.get('image')+")"

                                        options = child.answer.optionbox.find_all('option')
                                        for opt in options:
                                            option = ""
                                            if opt.get('text'):
                                                option = option + opt.get('text')
                                            if opt.get('image'):
                                                option = getOptionImage(opt, option, path, path_to_xml_dict)
                                            question_dict['all_answers'].append(option)
                                        question_dict['correct_answer'] = child.answer.optionbox.get('correct')
                                        level_dict['questions'].append(question_dict)

                    final_dict['children'].append(level_dict)
                else:
                    print("Directory "+level+" is not present")
        return final_dict

sample_tree = {}
sample_tree['title'] = "Hindi"
sample_tree['id'] = "Hindi"
sample_tree['description'] = "v1"
sample_tree['children'] = []
#for folder in ['Maths']:


for folder in ['Maths','Science','Unmapped_Content']:
    folder_dict = foldersCreationInJson(folder)
    path = path_of_content+folder+'/'
    temp_list = []
    if folder == 'Unmapped_Content':
        temp_list.extend(dict_structure2)
    else:
        temp_list.extend(dict_structure1)

    for subfolder in temp_list:
        subfolder_dict = foldersCreationInJson(subfolder)
        path1 = path + subfolder+'/'
        list_of_folder = os.listdir(path1)
        sorted_folder = []
        #print(list_of_folder)
        if folder == 'Unmapped_Content':
            sorted_folder.extend(list_of_folder)
        else:
            sorted_folder = sort_folders(list_of_folder)
        #print(sorted_folder)
        #for subfolder1 in ['1. Integers', '3. Data Handling', '4. Simple equations']:
        for subfolder1 in sorted_folder:
            subfolder_dict1 = foldersCreationInJson(subfolder1)
            path2= path1+subfolder1+'/'

            for subfolder2 in os.listdir(path2):
                subfolder_dict2 = foldersCreationInJson(subfolder2)
                path3 = path2+subfolder2+'/'
                print(subfolder2)
                if subfolder == 'Video':
                    for subfolder4 in os.listdir(path3):
                        subfolder_dict3 = foldersCreationInJson(subfolder4)
                        path4 = path3+subfolder4+'/'
                        for subfolder5 in os.listdir(path4):
                            if subfolder5.endswith('.mp4'):
                                subfolder_dict3['children'].append(video_node(path4, subfolder5))
                        subfolder_dict2['children'].append(subfolder_dict3)
                else:

                    for subfolder3 in os.listdir(path3):
                    #for subfolder3 in ['Quiz1','Quiz2','Quiz3','Quiz4','Quiz5']:
                        if subfolder3.endswith('.zip'):
                            zip_ref = zipfile.ZipFile(path3+subfolder3,'r')
                            zip_ref.extractall(path3)
                            zip_ref.close()
                            print("************Folder name",path3+subfolder3)
                            subfolder_dict2['children'].append(exercise_scrapping(subfolder3, path3))


                        elif subfolder3.endswith('.mp4'):
                            subfolder_dict2['children'].append(video_node(path3, subfolder3))

                subfolder_dict1['children'].append(subfolder_dict2)
            subfolder_dict['children'].append(subfolder_dict1)
        folder_dict['children'].append(subfolder_dict)
    sample_tree['children'].append(folder_dict)

print("Final Dict::--->", sample_tree)

SAMPLE_TREE1 = []
SAMPLE_TREE1.append(sample_tree)





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
        'CHANNEL_THUMBNAIL': CHANNEL_THUMBNAIL, # (optional) local path or url to image file
        #'CHANNEL_DESCRIPTION': 'A sample sushi chef to demo content types.',      # (optional) description of the channel (optional)
    }

    def construct_channel(self, *args, **kwargs):
        """
        Create ChannelNode and build topic tree.
        """
        channel = self.get_channel(*args, **kwargs)   # creates ChannelNode from data in self.channel_info
        _build_tree(channel, SAMPLE_TREE1)
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

            # mastery_model = (child_source_node.get('mastery_model') and {"mastery_model": child_source_node['mastery_model']}) or {}
            mastery_model = mastery_calculation(int(len(child_source_node.get("questions"))))
            child_node = nodes.ExerciseNode(
                source_id=child_source_node["id"],
                title=child_source_node["title"],
                license=child_source_node.get("license"),
                author=child_source_node.get("author"),
                exercise_data = mastery_model,
                description=child_source_node.get("description"),
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
