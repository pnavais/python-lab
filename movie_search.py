#!/usr/bin/env python3

# Copyright 2019 Pablo Navais
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import sys, getopt
import datetime
import time
import threading
import requests
import urllib.parse

#
# A little utility script to search movies using TheMovieDB REST API
# Usage : movie_search.py -a <MOVIE_DB_API_KEY> -n <MOVIE_NAME>
####################################################################

# Constants
# #########

RED          = "\u001b[31m"
YELLOW       = "\u001b[33m"
BLUE         = "\u001b[34m"
WHITE        = "\u001b[37m"
GREEN        = "\u001b[32m"
RESET        = "\u001b[0m"
BOLD         = "\u001b[1m"
UNDERLINE    = "\u001b[4m"
SAVE_CUR     = "\033[s"
RESET_CUR    = "\033[u"
CLEAR_RIGHT  = "\033[K"
CHECK_SYMBOL = "\u2713"
CROSS_SYMBOL = "\u274C"

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie?api_key=<api_key>&query=<query>&page=<page>"

# Globals
# #########

api_key     = ''
movie_name  = ''
movies_list = []
max_movies  = -1

"""
Return an ANSI red colored string
"""
def red(str):
	return RED+str+RESET

"""
Return an ANSI yellow colored string
"""
def yellow(str):
	return YELLOW+str+RESET

"""
Return an ANSI green colored string
"""
def green(str):
	return GREEN+str+RESET

"""
Return an ANSI bold colored string
"""
def bold(str):
	return BOLD+str+RESET

"""
Displays help syntax
"""
def showHelp():
	print(yellow("Usage : ")+os.path.basename(__file__)+" [-a <api_key>] [-n <movie_name>] [-h]")
	print("\nWhere :")
	print("\t-a, --api:  the MovieDB API key")
	print("\t-n, --name: the name of the movie to search")
	print("\t-m, --max:  the maximum number of movies to show")
	print("\t-h, --help: this help")

"""
Parses the command line input
and retrieves the actual parameters.
"""
def parseCmd(argv):
	global api_key
	global movie_name
	global max_movies

	try:
		opts, args = getopt.getopt(argv,"ha:n:m:",["help","api=","name=","max="])
	except getopt.GetoptError as e:	
		print("\n"+red(str(e))+"\n", file=sys.stderr)
		showHelp()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			showHelp()
			sys.exit(0)
		elif opt in ("-a", "--api"):
			api_key = arg
		elif opt in ("-n", "--name"):
			movie_name = arg
		elif opt in ("-m", "--max"):
			max_movies = int(arg) if arg.isdigit() else 0

	if not (api_key):
		print(red("Missing MovieDB API key"))
		sys.exit(3)

	if not (movie_name):
		print(red("Missing Movie Name"))
		sys.exit(4)
	if (max_movies == 0):
		print(red("Invalid maximum number of movies"))
		sys.exit(5)

"""
Simply displays a waiting message
until interrupted or nmovies found
"""
def waitLoop():
	global movies_list

	try:
		while not movies_list:
			for j in range(0,3):				
				sys.stdout.write(".")
				sys.stdout.flush()
				time.sleep(0.3)	
			sys.stdout.write(RESET_CUR)
			sys.stdout.write(CLEAR_RIGHT)
			sys.stdout.flush()
			time.sleep(0.5)
	except:
		pass

	sys.stdout.write(RESET_CUR)
	sys.stdout.write(CLEAR_RIGHT)
	symbol=green(CHECK_SYMBOL) if movies_list else red(CROSS_SYMBOL)
	sys.stdout.write(symbol)
	sys.stdout.flush()

"""
Find the given movie
"""
def findMovie(api_key, movie_name, max_movies):

	try:
		current_page = 1
		more_pages = True
		search_url = re.sub("<api_key>", api_key, MOVIE_DB_SEARCH_URL)
		base_search_url = re.sub("<query>", urllib.parse.quote(movie_name, safe=''), search_url)
		
		while more_pages:
			search_url = re.sub("<page>", str(current_page), base_search_url)
			resp = requests.get(search_url)
			if resp.status_code == 200:	
				r_json = resp.json();
				total_pages = r_json['total_pages']			
			
				movies_result = r_json['results'];
				for movie in movies_result:
					try:
						date_time = datetime.datetime.strptime(movie['release_date'], '%Y-%m-%d')
						year = str(date_time.date().year)
					except:
						year = "????"
						pass						
					movies_list.append(movie['title']+" - ("+year+")")
					if ((max_movies>0) and (len(movies_list)>=max_movies)):
						break
				current_page+=1
				more_pages = (current_page<=total_pages)				
			else:
				more_pages = False
			if ((max_movies>0) and (len(movies_list)>=max_movies)):
				break

	except Exception as e:
		print("Error processing request : "+str(e))

	return movies_list

""" Main function """
def main(argv):
	parseCmd(argv)	
	sys.stdout.write("Searching movie ["+green(movie_name)+"] ")
	sys.stdout.flush()
	sys.stdout.write(SAVE_CUR)	
	time.sleep(1)

	# Launch the movie search thread
	t = threading.Thread(target=waitLoop)
	t.start()

	movies_list = findMovie(api_key, movie_name, max_movies)
	t.join()


	if movies_list:
		movies_list_size = len(movies_list);
		res_name = "result" if movies_list_size == 1 else "results"

		print("\n\n"+yellow(str(movies_list_size)+" "+res_name+" found :"))
		i=1;
		for movie in movies_list:
			print("[%d]"%i+" "+movie)
			i+=1;
	else:
		print("\n\nNo results found")


# Main entry point
if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	except KeyboardInterrupt as e:
		sys.exit(0)
