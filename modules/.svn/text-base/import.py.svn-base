import csv, os, sqlite3, sys, time, sherpa
from datetime import date

class publicationsDatabase(object):
	""" Variables of Note:
	scriptPath: 			Working directory of the python script
	databasePath: 			Directs to the script's permissions database
	inputPath / inputFile: 		The path to the file provided as a parameter to the script.
					if no file was provided, this will default to an import.txt 
					within the scripts working directory		
	dataload:			If the file name is import.txt this will be set to True
					When True, the script will verify the import.txt is a valid
					import file and then import the provided data into the database
					When False, the script will act as a lookup against the database
	"""

	def __init__(self, fileLocations):
		self.scriptPath = os.path.dirname(os.path.realpath(__file__))
		
		self.database = None
		self.databasePath = os.path.join(self.scriptPath, "db.sqlite3")

		self.countJournalsAdded = 0 
		self.countISSNsAdded = 0
		self.countPublishersAdded = 0
		self.countAgreementsAdded = 0
		
		if len(fileLocations) == 1:
			self.inputPath = self.scriptPath
			self.inputFile = "import.txt"
			print("No file provided: Using import.txt in program directory.\n")
			
		elif len(fileLocations) == 2:
			self.inputPath, self.inputFile = os.path.split(fileLocations[1])
			
		else:
			sys.exit("Error, Too many parameters")
				
	def connect(self):
		try:
			self.database = sqlite3.connect(self.databasePath)
			
			self.cursor = self.database.cursor()

		except sqlite3.Error as e:
			print("Error {}".format(e.args[0]))
			
			input("Press Enter to Exit.")
			sys.exit(1)
	
	def disconnect(self):
		self.database.commit()
		self.database.close()

	def buildImportData(self, journal_record):
		print("----------")
		print("Gathering Sherpa Data")
		print("----------")
			

		try:
			journal_record['ignore'] = False

			sherpa_results = sherpa.AskSherpa(journal_record['issn'])

			if isinstance(sherpa_results['journal'], basestring):
				journal_record['journal'] = unicode(sherpa_results['journal'])
			else:
				journal_record['journal'] = unicode(sherpa_results['journal'][0])


			if isinstance(sherpa_results['publisher'], basestring):
				journal_record['publisher'] = unicode(sherpa_results['publisher'])
			else:
				journal_record['publisher'] = unicode(sherpa_results['publisher'][0])

			if isinstance(sherpa_results['publisher_url'], basestring):
				journal_record['publisher_url'] = sherpa_results['publisher_url']
			else:
				journal_record['publisher_url'] = sherpa_results['publisher_url'][0]

		except:
			journal_record['ignore'] = True
			print "Unexpected error:", sys.exc_info()[0]
			

		return journal_record
		
	def loadData(self):	
		imported_journals = []

		try:
			with open(os.path.join(self.inputPath, self.inputFile), 'r') as openFile:
				for row in openFile:
					temp = row.replace("\t\t", "\t \t").replace("'", "''").replace("\n", "").split('\t')
					for item in temp:
						if item == ' ':
							item = ""

					imported_journals.append(dict(evidence_url=temp[1], version=temp[2], embargo=temp[3], notes=temp[4], issn=temp[5]))
		except IOError:
			sys.exit("That file doesn't exist!")
		
		print("----------")
		print("Generating Database Entries")
		print("----------")

		for index, importItem in enumerate(imported_journals):
			print("\n{} of {}".format(index+1, len(imported_journals)))


			print("Processing '{issn}'".format(**importItem))
			print("Check DB for ISSN")

			command = "SELECT (1) FROM permission_issn WHERE issn =? limit 1" #Check to see if ISSN currently exists within database
			
			if not self.cursor.execute(command, (importItem['issn'],)).fetchall(): #If record doesn't exist within database
				print("Not Found.")
				# collect Sherpa details
				importItem = self.buildImportData(importItem)
				if importItem['ignore']:
					continue

				print("Checking DB for Journal {}".format(importItem['journal'].encode('utf-8')))
				command = "SELECT * FROM permission_journal WHERE title = ?"
				queryResults = self.cursor.execute(command, (importItem['journal'],)).fetchall()
				
				if queryResults:
					# Insert ISSN
					print(" * Adding ISSN: {issn}".format(**importItem))
					command = "INSERT INTO permission_issn VALUES (NULL, ?, ?)"
					self.cursor.execute(command, (importItem['issn'], queryResults[0][0]))
					self.countISSNsAdded += 1
					
					continue
	
				else:
					print("Not Found. \n Checking for Publisher '{}'".format(importItem['publisher'].encode('utf-8')))
					# Check if Publisher Exists
					command = "SELECT * FROM permission_publisher WHERE name = ?"
					result = self.cursor.execute(command, (importItem['publisher'],)).fetchall()
					
					if result:
						print("Publisher Found.")
						# Keep track of publisher for use in agreement / journal
						importItem['publisher_id'] = result[0][0]

					else:
						# Create publisher and keep track of publisher
						if not importItem['publisher_url']:
							continue

						print(" * Adding Publisher: {}".format(importItem['publisher'].encode('utf-8')))
			
						command = "INSERT INTO permission_publisher VALUES (NULL, ?, ?)"
						self.cursor.execute(command, (importItem['publisher'], importItem['publisher_url']))
						self.countPublishersAdded += 1

						importItem['publisher_id'] = self.cursor.lastrowid

					#See if the agreement exists
					if importItem['evidence_url'] == "As Per Article":
						print("Evidence 'As Per Article', Skipping")
						continue

					print("Searching for Agreement with Evidence at '{evidence_url}'".format(**importItem))

					command = "SELECT * FROM permission_agreement WHERE evidence_location = '{evidence_url}'".format(**importItem)
					result = self.cursor.execute(command).fetchall()

					if result:
						print("Agreement Found.")
						# Keep track of agreement
						importItem['agreement_id'] = result[0][0]
						if result[0][1] == 1:
							command = "UPDATE permission_agreement SET journal_only=0 WHERE id=?"
							self.cursor.execute(command, (result[0][0],))
						

					else:
						# Create agreement
						importItem['submitted'] = 0
						importItem['submitted_restrictions'] = ""
						importItem['accepted'] = 0
						importItem['accepted_restrictions'] = ""
						importItem['published'] = 0
						importItem['published_restrictions'] = ""

						temp_version = importItem['version'].lower()
						temp_embargo = temp_version + "_restrictions"
						importItem[temp_version] = 1
						importItem[temp_embargo] = importItem['embargo']

						evidence_statement = "BULK LOADED. PLEASE UPDATE"
						
						print(" Agreement not found. \n * Adding Agreement")
						
						try:
							# "INSERT INTO permission_agreement VALUES (NULL, 1, '{accepted}', '{accepted_restrictions}', '{submitted}', '{submitted_restrictions}', '{published}', '{published_restrictions}', '', '{notes}', '{evidence_statement}', '{evidence_url}', 'HTML', '2008-11-11', {publisher_id})"
							command = "INSERT INTO permission_agreement VALUES (NULL, 1, ?, ?, ?, ?, ?, ?, '', ?, ?, ?, 'HTML', '2008-11-11', ?)".format(evidence_statement, **importItem)
							self.cursor.execute(command, (importItem['accepted'], importItem['accepted_restrictions'], importItem['submitted'], importItem['submitted_restrictions'], importItem['published'], importItem['published_restrictions'], importItem['notes'], evidence_statement, importItem['evidence_url'], importItem['publisher_id']))

						except:
							command = "INSERT INTO permission_agreement VALUES (NULL, 1, ?, ?, ?, ?, ?, ?, '', '', ?, ?, 'HTML', '2008-11-11', ?)".format(evidence_statement, **importItem)
							self.cursor.execute(command, (importItem['accepted'], importItem['accepted_restrictions'], importItem['submitted'], importItem['submitted_restrictions'], importItem['published'], importItem['published_restrictions'], evidence_statement, importItem['evidence_url'], importItem['publisher_id']))
				

						self.countAgreementsAdded += 1
									
						importItem['agreement_id'] = self.cursor.lastrowid

					print(" Journal not found. \n *  Adding: '{}'".format(importItem['journal'].encode('utf-8')))

					command = "INSERT INTO permission_journal VALUES (NULL, ?, 'BULK LOAD', ?, ?)"
					self.cursor.execute(command, (importItem['journal'], importItem['publisher_id'], importItem['agreement_id']))
					
					self.countJournalsAdded +=1

					importItem['journal_id'] = self.cursor.lastrowid					

					print("Adding ISSN: {}".format(importItem['issn']))
					command = "INSERT INTO permission_issn VALUES (NULL, ?, ?)"

					self.cursor.execute(command, (importItem['issn'], importItem['journal_id']))
					self.countISSNsAdded += 1

					self.database.commit()

			print("ISSN Found.")

		print("This session: \n {} Publishers Added. \n {} Agreements Added. \n {} Journals Added. \n {} ISSNs Added \n".format(self.countPublishersAdded, self.countAgreementsAdded, self.countJournalsAdded, self.countISSNsAdded))
	
	def run(self):
		self.connect()
		self.loadData()
		self.disconnect()
		

if __name__ == '__main__':
	program = publicationsDatabase(sys.argv)
	program.run()
