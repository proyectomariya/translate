# -*- coding: utf-8 -*-
import os
from os import _exit;
from threading import Thread

import RPi.GPIO as pin

# Modules required by record audio
import pyaudio
import wave
import time 

# Modules required by Speech to text
import json
import urllib2

# Modules required by translate
import sqlite3 as sql
import unicodedata

# Modules required by Text to speech
from gtts import gTTS

# Variables required by Raspberry
PIN_NUMBER_BUTTON = 18
PIN_NUMBER_LED = 17
PIN_NUMBER_SWITCH = 27

# Variables required by record audio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "record.wav"

# Variables required by translate
CONNECTION = sql.connect("/home/pi/Desktop/database/translate.db")
HE_FILE = "temp.txt"

# Variables required by Google Speech to text
WAV_SOURCE = 'record.wav'
FLAC_SOURCE = 'source.flac'
UNDERSTAND_ERROR = "No te entendi, porfavor repite."
API_ERROR = "Ha ocurrido un error al tratar de entenderte. intenta de nuevo"
DB_ERROR = "No encontre registro en la base de datos."

# Variables required by Text to speech
LANG = 'es'


# Initialize raspberry GPIO
pin.setmode(pin.BCM)
pin.setup(PIN_NUMBER_BUTTON, pin.IN, pull_up_down = pin.PUD_UP)
pin.setup(PIN_NUMBER_LED, pin.OUT)
pin.setup(PIN_NUMBER_SWITCH, pin.IN, pull_up_down = pin.PUD_UP)

#################################################################################################

# Convert the wav source to a flac source
def convert_to_flac():
	os.system("avconv -i " + WAV_SOURCE + " -y -ar 16000 " + FLAC_SOURCE) 

# Transcribe recording  produced by the user
def speech_to_text(language):
	convert_to_flac()
	url = 'http://www.google.com/speech-api/v2/recognize?output=json&lang=%s&maxresults=5&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw'%(language)
	body = open(FLAC_SOURCE, 'rb').read()
	filesize = os.path.getsize(FLAC_SOURCE)	

	req = urllib2.Request(url=url)
	req.add_header('Content-type','audio/x-flac; rate=16000')
	req.add_header('Content-length', str(filesize))
	req.add_data(body)
	try:
		response = urllib2.urlopen(req)
		response_text = response.read().decode('utf-8')
		#Ignore any blank blocks
		actual_result = []
		for line in response_text.split("\n"):
			if not line: continue
			result = json.loads(line)["result"]
			if len(result) != 0: 
				actual_result = result[0]
				break
		try:
			if len(actual_result.get("alternative", [])) == 0:
				return None, None
		except:
			print "ERROR EN LEN ACTUAL RESULT :GET "
			print actual_result
			return None, None
		try:
			best_hypothesis = max(actual_result["alternative"], key=lambda alternative: alternative["confidence"])
		except:
			return None, None
		if "transcript" not in best_hypothesis:
			return None, None
		return best_hypothesis["transcript"], actual_result
	except urllib2.HTTPError, e:
		error_message = e.read()
	except urllib2.URLError, e:
		error_message = e.reason
	return generate_audio(API_ERROR)

#################################################################################################

# Delete tildes 
def delete_tildes(understand_word):
	s = ''.join((c for c in unicodedata.normalize('NFD',unicode(understand_word)) if unicodedata.category(c) != 'Mn'))
	return s.decode().lower()

# Search a word or a phrase in the data base
def search_data(string, idiom_code):
	global CONNECTION
	# search data to translate Espanish to Huichol 
	if idiom_code == 1:
		query = 'SELECT huichol_word FROM words_huichol WHERE id = (SELECT id FROM words_spanish WHERE spanish_word = "' + string + '");'
	# Search data to translate Huichol to Espanish 
	else:
		query = 'SELECT spanish_word FROM words_spanish WHERE id = (SELECT id_espanol FROM words_pronuntation WHERE pronuntation = "' + string + '");'

	data_found = []
	with CONNECTION:
		cur = CONNECTION.cursor()
		cur.execute(query)
		data_found = cur.fetchmany(size=1)
		#data_found = cur.fetchall()

	if len(data_found) > 0:
		return clean_data(data_found)
	return None

# Search data return with a specific format so we need clean the data
def clean_data(result):
	clean_data = str(result[0])
	clean_data = clean_data[3:-3]
	return clean_data

# Translate a word or phrase, if phrase not match, parse and find word by word and then join the final answer
def translate_data(word_or_phrase, mode):
	# Search if we can find the word or phrase directly
	if mode == 0:
		result = search_data(word_or_phrase, mode)
	else:
		result = search_data(delete_tildes(word_or_phrase), mode)

	if result is not None:
		return result
	if mode == 1:
		list_of_words = word_or_phrase.split()
		if len(list_of_words) > 1:
			translation = ""
			for word in list_of_words:
				result = search_data(delete_tildes(word), mode)
				if result is not None:
					translation += result + " "
			if translation != "":
				return translation
	return None

#################################################################################################

# Generate audio and play it using the gtts API
def generate_audio(string):
	# Generate
	tts = gTTS(text=string, lang=LANG)
	tts.save("output.mp3")
	# Play 
	os.system('mplayer output.mp3')

#################################################################################################

def translate_EH():
	# Get the result of speech to text
	google_answer, google_answers =  speech_to_text("es-MX")

	if google_answer is None and google_answers is None:
		return generate_audio(UNDERSTAND_ERROR)

	print google_answer

	# Get the hypothesis translate 
	translate = translate_data(google_answer, 1)

	# Suppose we have result, generate audio with the translation
	if translate is not None:
			return generate_audio(translate)
	else:
		for answer in google_answers["alternative"]:
			translate = translate_data(answer["transcript"], 1)
			# Suppose we have result, generate audio with the translation
			if translate is not None:
				return generate_audio(translate)
	# If we cannot find a translate return error
	return generate_audio(DB_ERROR)

def tranlate_HE():
	content = None
	traduction = ""
	# Save all lines of file in a list 
	with open(HE_FILE) as f:
		content = f.readlines()

	# Translate each line, line by line and join it 
	for line in content:
		print "LINE HE: " + line.strip("\n") 
		translate = translate_data(line.strip("\n"), 0)
		if translate is not None:
			traduction += translate + " "

	# Delete file 
	delete_STTresult_file()

	# Play traduction
	if traduction != "":
		return generate_audio(traduction)
	return generate_audio(DB_ERROR)

#################################################################################################

def save_STTresult_file(language):
	file = open(HE_FILE, "a")
	google_answer, google_answers = speech_to_text(language)
	if google_answer is not None and google_answers is not None:
		file.write(google_answer + "\n")
		for answer in google_answers["alternative"]:
			if answer != google_answer:
				file.write(answer["transcript"] + "\n")
	file.close()

def delete_STTresult_file():
	os.system('rm temp.txt')

# Save the record, wav format 
def save_record(audio, frames):
	waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()

def blink_led(times, time_s):
	for i in range(0, times):
		time.sleep(time_s)
		pin.output(PIN_NUMBER_LED, pin.HIGH)
		time.sleep(time_s)
		pin.output(PIN_NUMBER_LED, pin.LOW)

while True:
	time.sleep(0.2)
	pin.wait_for_edge(PIN_NUMBER_BUTTON, pin.FALLING)
	switch_mode = 1
	if pin.input(PIN_NUMBER_SWITCH) == pin.LOW:
		switch_mode = 0
	# Start take time
	start = time.time()
	
	# initialize microphone
	audio = pyaudio.PyAudio()
	stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
	frames = []

	print "Start recording..."
	while pin.input(PIN_NUMBER_BUTTON) == pin.LOW:
		pin.output(PIN_NUMBER_LED, pin.HIGH)
		time.sleep(0.01)
		# Save data from microphone
		data = stream.read(CHUNK)
		frames.append(data)

	pin.output(PIN_NUMBER_LED, pin.LOW)
	# Stop recording 
	stream.stop_stream()
	stream.close()
	audio.terminate()

	# Save record
	save_record(audio, frames)

	# Guardar el tiempo que se mantuvo presionado
	length = time.time() - start
	print "TIEMPO PRESIONADO :" +  str(length)

	if(length < 0.3):
		# El LED se apaga
		# Confirmamos que halla archivos
		if os.path.exists(HE_FILE):
			# La traduccion comienza y se ignora la ultima grabacion
			if(switch_mode != 1):
				tranlate_HE()
	else:
		# Espanish to huichol translate begin
		if(switch_mode == 1):
			translate_EH()
		else:
			save_STTresult_file("en-US")
			blink_led(3,0.15)
			print("Esperamos la siguiente palabra")
			# El LED comieza a parpadear
			# En brackground se guarda el resultado de STT  de HE
			
			#brackground_thread = Thread(target=save_STTresult_file, args=("en-US",))
			#brackground_thread.start() 

_exit(0)
