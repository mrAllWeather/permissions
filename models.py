import datetime
import sys
from django.utils import timezone
from django.db import models
from django.core.exceptions import MultipleObjectsReturned
import modules.sherpa as sherpa

# Create your models here.
class Publisher(models.Model):
	name = models.CharField(max_length=200, unique=True)
	website = models.CharField(max_length=200, blank=True)

	def journals(self):
		output = Journal.objects.filter(publisher_id=self.id)
		return output

	def agreements(self):
		output = Agreement.objects.filter(publisher=self.id)
		return output

	def __unicode__(self):
		return self.name

	class Meta:
		ordering = ['name',]

class Agreement(models.Model):
	EVIDENCE_FORM_CHOICES = (
		('HTML', 'Web Link'),
		('LOCAL', 'Intranet Folder'),
		('TRIM', 'TRIM Storage'),
	)
	
	journal_only = models.BooleanField('Journal Agreement', default=True)
	accepted = models.BooleanField()
	accepted_restrictions = models.CharField(max_length=200, blank=True, help_text='embargo period in months')
	submitted = models.BooleanField()
	submitted_restrictions = models.CharField(max_length=200, blank=True, help_text='embargo period in months')
	published = models.BooleanField()
	published_restrictions = models.CharField(max_length=200, blank=True, help_text='embargo period in months')
	description = models.CharField('Agreement Description', max_length=50, blank=True, help_text='Use: Describe "publisher wide" agreement for easy searching. eg. "Health and Medical journals only"')
	notes = models.TextField(max_length=500, blank=True, help_text='Use: Non-embargo restrictions on deposit of Full-Text')
	evidence_statement = models.TextField(max_length=1500, help_text='Use: Evidence supporting deposit as it would appear on Copyright Coversheet')
	evidence_location = models.CharField(max_length=200, unique=True)
	evidence_form = models.CharField(max_length=5, choices=EVIDENCE_FORM_CHOICES, default='HTML')
	verified = models.DateField(auto_now=True)
	publisher = models.ForeignKey(Publisher)

	def __unicode__(self):
		output = ""
		if(self.journal_only):
			try:
				output += unicode(Journal.objects.get(agreement_id=self.id)) + ": "
			except: #Always triggers the first time (the journal hasn't had the agreement attached yet!)
				output += "No Attached Journal: "
		else:
			output += unicode(self.publisher.name) + ": " + (self.description)
			return unicode(output)

		if(self.published):
			if(self.published_restrictions==""):
				output += 'Published. '
			else:
				output += 'Published with Provisions. '
		elif(self.accepted):
			if(self.accepted_restrictions==""):
				output += 'Accepted. '
			else:
				output += 'Accepted with Provisions. '
		elif(self.submitted):
			if(self.submitted_restrictions==""):
				output += 'Submitted.'
			else:
				output += 'Submitted with Provisions.'
		if(not(self.published or self.accepted or self.submitted)):
			output += 'No Formal Permissions'

		return unicode(output)

	__unicode__.admin_order_field = 'publisher'

	def last_verified(self):
		age = datetime.date.today() - self.verified
		if (age.days > 365):
			return unicode('%s year/s ago' % (age.days // 365))
		elif(age.days > 31):
			return unicode('%s month/s ago' % (age.days // 31))
		elif(age.days > 7):
			return unicode('%s week/s ago' % (age.days // 7))
		elif(age.days > 0):	
			return unicode('%s day/s ago.' % age.days)
		else:
			return unicode('Today.')

	last_verified.admin_order_field = 'verified'

		
class Journal(models.Model):
	title = models.CharField(max_length=200)
	website = models.CharField(max_length=200, blank=True)
	publisher = models.ForeignKey(Publisher)
	agreement = models.ForeignKey(Agreement)

	def __unicode__(self):
		return self.title

	def issn(self):
		output = ISSN.objects.filter(journal_id=self.id)
		return output

	def first_letter(self):
		return self.title and self.title.upper()[0] or ''



	def sherpa_results(self):
		try:
			issn = unicode(ISSN.objects.get(journal_id=self.id))
			print("Connect to Sherpa: Request['" + unicode(ISSN.objects.get(journal_id=self.id)) + "']")
			output = sherpa.AskSherpa(issn)
			return output

		except MultipleObjectsReturned:
			issn = ISSN.objects.filter(journal_id=self.id)
			issn = unicode(issn[0])
			print("Connect to Sherpa: Request['" + issn + "']")
			print("Multiple ISSNs Found")
			output = sherpa.AskSherpa(issn)
			return output

		except:
			print("Connect to Sherpa: No Results"), sys.exc_info()[0]
			return "None Available:", sys.exc_info()[0]
		


class ISSN(models.Model):
	issn = models.CharField(max_length=13)
	journal_id = models.ForeignKey(Journal)

	def __unicode__(self):
		return self.issn

