import re
import urllib.request
import numpy as np
import openai
from gtts import gTTS
from moviepy.editor import *

from apikey import apikey

openai.api_key = apikey

screen_width = 256
screen_size = (screen_width, screen_width)

# Clear then create working directories
working_dir = './working/'
for root, dirs, files in os.walk(working_dir, topdown=False):
    for name in files:
        os.remove(os.path.join(root, name))
    for name in dirs:
        os.rmdir(os.path.join(root, name))
sub_working_dirs = ['audio', 'image', 'video']
for sub_working_dir in sub_working_dirs:
    os.makedirs(working_dir + sub_working_dir)


# Takes prompt and returns written story
def write_story(story_idea):
    full_prompt = f"Write a short story about the following: {story_idea}"
    # Call openai to complete story
    completions = openai.Completion.create(
        model="text-babbage-001",
        prompt=full_prompt,
        max_tokens=256,
        temperature=0.6
    )
    return completions.choices[0].text


# Call DALL E for image and return
def create_image(ix, chunk):
    image_filepath = f"working/image/image{ix:03}.jpg"
    try:
        dalle_response = openai.Image.create(
            prompt=chunk.strip(),
            n=1,
            size=str(screen_size[0]) + "x" + str(screen_size[1])
        )
        # Fetch and save image
        image_url = dalle_response['data'][0]['url']
        print("IMAGE URL:", image_url)
        urllib.request.urlretrieve(image_url, image_filepath)
    except openai.error.InvalidRequestError:  # If DALL E refuses prompt
        image = np.full((screen_size[0],screen_size[1],3), 0, dtype=np.uint8)
        imageio.imwrite(image_filepath, image)
    return image_filepath


# Call gTTS for audio and return
def gen_audio(ix, chunk):
    audio_filepath = f"working/audio/voiceover{ix:03}.mp3"
    tts = gTTS(text=chunk, lang='en', slow=False)
    tts.save(audio_filepath)
    return audio_filepath


def generate(story_idea):
    story = write_story(story_idea)
    # Split the text at every comma and period
    chunked_story = re.split(r"[,.]", story)
    clips = []
    for ix, chunk in enumerate(chunked_story[:-1]):
        chunk = chunk.strip()
        image_filepath = create_image(ix, chunk)
        audio_filepath = gen_audio(ix, chunk)
        audio_clip = AudioFileClip(audio_filepath)
        audio_duration = audio_clip.duration
        image_clip = ImageClip(image_filepath).set_duration(audio_duration)
        text_clip = TextClip(
            chunk, size=screen_size, color="white", stroke_color="black", font="Liberation-Mono", stroke_width=1, method="caption"
        )
        text_clip = text_clip.set_position('center').set_duration(audio_duration)
        audio_image_clip = image_clip.set_audio(audio_clip)
        video = CompositeVideoClip([audio_image_clip, text_clip])
        clips.append(video)
    final_video = concatenate_videoclips(clips, method="compose")
    smallurl = story_idea + ".mp4"
    url = "static/" + smallurl
    final_video = final_video.write_videofile(url, fps=24)
    return smallurl


