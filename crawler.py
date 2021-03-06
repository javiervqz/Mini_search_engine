#Initialize libraries
import sqlite3
from webParser import LinkParser
import sys
import time
#End Libraries



conn = sqlite3.connect('DataBases/Fing.db')
cur = conn.cursor()
#Create schema for DB
cur.executescript('''
CREATE TABLE IF NOT EXISTS Pages(
id INTEGER PRIMARY KEY,
url TEXT UNIQUE,
html TEXT,
error INTEGER,
old_rank REAL,
new_rank REAL,
id_website INTEGER
);

CREATE TABLE IF NOT EXISTS Websites(
id INTEGER PRIMARY KEY,
url TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Links(
from_id INTEGER,
to_id INTEGER
)
''')

#Cleaning input url outputs html and url
web_site = input('Type website to crawl\n')
many = int(input('How many?\n'))
BaseWeb = LinkParser()
html, BaseUrl = BaseWeb.CleanUrl(web_site)

cur.execute('''SELECT * FROM Websites WHERE url LIKE ?''', ('%'+web_site+'%',))
row = cur.fetchone()

if row is None:
	cur.execute('''
				INSERT OR IGNORE
				INTO Websites (url) VALUES (?)''', (BaseUrl,))
	cur.execute('''SELECT id FROM Websites''')
	id_website = cur.fetchone()[0]
	cur.execute('''INSERT OR IGNORE
				INTO Pages (url, html, new_rank, id_website, error)
				VALUES (?, ?, 1.0, ?, 120)
				''', (BaseUrl,memoryview(html), id_website))
else:
	id_website = row[0]
	print('Restarting existing crawl \n')

i = 0
while_starts = time.time()
while i < many:
	print(i + 1, '\n')
	links = []
	cur.execute('''
				SELECT html, url FROM Pages WHERE error = 120
				ORDER BY RANDOM() LIMIT 1''')
	row = cur.fetchone()
	if row is None:
		print('No more pages to visit')
		break
	html = row[0]
	BaseUrl = row[1]
	print('Getting links from page {}'.format(BaseUrl))
	print ('{}, {}'.format(len(html), BaseUrl))
	cur.execute('''
				UPDATE Pages SET error = 100 WHERE url = ? ''', (BaseUrl,))
	links = BaseWeb.GetLinks(html,web_site)
	#links = unique(links)


	cur.execute('''SELECT id FROM Pages WHERE url = ? ''', (BaseUrl,))
	from_id = cur.fetchone()[0]
	print ('Links found',len(links))
	j = 0

	for_starts = time.time()
	for link in links:
		try:
			try:
				html, BaseUrl = BaseWeb.CleanUrl(link)
			except:
				continue
			if BaseUrl == "Not html page":
				print ("Ignored page (not html)")
				continue
			elif html is None:
				cur.execute('''
							INSERT OR IGNORE INTO Pages (url, error)
							VALUES (?, 150)''', (BaseUrl,))
			else:
				cur.execute('''
							INSERT OR IGNORE INTO
							Pages (url, html, new_rank, id_website, error)
							VALUES (?, ?, 1.0, ?, 120)
							''', (BaseUrl, html, id_website))

			cur.execute('''SELECT id FROM Pages WHERE url = ? ''', (BaseUrl,))
			to_id = cur.fetchone()[0]
			if from_id != to_id:
				cur.execute('''
							INSERT INTO Links (from_id, to_id)
							VALUES (?, ?)''', (from_id, to_id))
				continue
			j += 1
		except KeyboardInterrupt:
			print ('Program Interrupted')
			break

	for_ends = time.time()
	print ('It took to get links ' + str(for_ends - for_starts)+ 's\n')
#	conn.commit()

	i += 1
while_ends = time.time()
print ('It took to find finish the program ' + str(while_ends - while_starts)+ 's\n')


conn.commit()
cur.close()
