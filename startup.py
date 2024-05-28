import os
import time
import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment
from tqdm import tqdm

# read the text from the strings.txt file and save it into a global list
strings = []

def get_text_from_url(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup.get_text()
        except Exception as e:
            print(f"An error occurred while fetching URL: {url}")
            print(f"Error details: {e}")
        # Wait for a moment before retrying
        time.sleep(5)
    print(f"Failed to get text from URL after {max_retries} attempts: {url}")
    return None

def remove_text_between(string, start, end):
    """
    Removes all the text between the first occurrence of 'start' and 'end' in 'string'.
    
    Args:
        string (str): The input string.
        start (str): The starting substring.
        end (str): The ending substring.
    
    Returns:
        str: The modified string with the text removed.
    """
    # Find the index of the first occurrence of 'start'
    start_index = string.find(start)
    
    # If 'start' is not found, return the original string
    if start_index == -1:
        return string
    
    # Find the index of the first occurrence of 'end' after 'start'
    end_index = string.find(end, start_index + len(start))
    
    # If 'end' is not found after 'start', return the original string
    if end_index == -1:
        return string
    
    # Remove the text between 'start' and 'end'
    result = string[:start_index] + ":" + string[end_index + len(end):]
    
    return result


def clean_text(text, chapter_num):
    for string in strings:
        text = text.replace(string, "")

    chapter_count = text.count("Chapter")

    counts = [0, 1]

    if chapter_count in counts:
        # find the first instance of "play"
        play_index = text.find("Play")

        # remove the text before "play"
        text = text[(play_index + len("play")):]

        if chapter_count == 0:
            text = "Chapter "+ str(chapter_num) + text
    else:
        print(f"Chapter {chapter_num} has multiple chapter headings")
        print(f"Chapter count: {chapter_count}")

        # save the text to a file
        text_file = f"AEDD_{chapter_num}.txt"
        with open(text_file, "w", encoding="utf-8") as file:
            file.write("Number of chapter headings: " + str(chapter_count) + "\n\n")
            file.write(text)


    return text

def processChapters (start, end):
    text = ""
    for chapter_num in range(start, end + 1):
        url = f"https://wuxia.click/chapter/alchemy-emperor-of-the-divine-dao-{chapter_num}"
        webpage_text = get_text_from_url(url)
        if webpage_text:
            cleaned_text = clean_text(webpage_text, chapter_num)
            text += cleaned_text + "\n\n"
        else:
            pass
    return text

def merge_audio_files(audio_files, output_file):
    merged_audio = AudioSegment.empty()

    for audio_file in audio_files:
        segment = AudioSegment.from_file(audio_file, format="mp3")
        merged_audio += segment

    merged_audio.export(output_file, format="mp3")

if __name__ == "__main__":
    start = int(input("Enter the starting chapter number: "))
    end = int(input("Enter the ending chapter number: "))
    interval = 50

    with open("strings.txt", "r") as file:
        for line in file:
            strings.append(line.strip())

    for i in range(start, end + 1, interval):
        print(f"Processing chapters {i} to {min(i + interval - 1, end)}...")
        
        text = processChapters(i, min(i + interval - 1, end))

        # save the text to a file
        text_file = f"AEDD_{i}_to_{min(i + interval - 1, end)}.txt"
        with open(text_file, "w", encoding="utf-8") as file:
            file.write(text)
