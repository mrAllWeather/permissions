import sys
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.sites.models import get_current_site

from permission.models import Journal, Agreement, ISSN, Publisher
# Create your views here.
def index(request):
	journals = Journal.objects.all().extra(
		select={'lower_name': 'lower(title)'}).order_by('lower_name')
	context = {'journals': journals}
	return render(request, 'permission/index.html', context)

def publisher_index(request):
	publishers = Publisher.objects.all().extra(
		select={'lower_name': 'lower(name)'}).order_by('lower_name')
	context = {'publishers': publishers}
	return render(request, 'permission/pub_index.html', context)

def publisher_detail(request, publisher_id):
	publisher = get_object_or_404(Publisher, pk=publisher_id)
	domain_name = get_current_site(request)
	domain_name = domain_name.domain
	return render(request, 'permission/pub_details.html', {'publisher': publisher, 'domain_name': domain_name})

def detail(request, journal_id):
	journal = get_object_or_404(Journal, pk=journal_id)
	domain_name = get_current_site(request)
	domain_name = domain_name.domain
	return render(request, 'permission/details.html', {'journal': journal, 'domain_name': domain_name})

def results(request, journal_id):
	return HttpResponse("You are looking at the results of journal %s" % journal_id)

def vote(request, journal_id):
	return HttpResponse("You are voting on journal %s" % journal_id)

def search(request):
	errors = []


	domain_name = get_current_site(request)
	domain_name = domain_name.domain

	if 'query' in request.GET:
		query = request.GET['query']
		if not query:
			errors.append('No ISSN entered')
		elif len(query) != 9:
			errors.append('Please keep the issn to 9 characters. eg 1111-1111')
		else:
			try:
				for index, letter in enumerate(query):
					if index == 4:
						if letter != '-':
							errors.append('Malformed ISSN. ISSN is 8 numbers with a - in the middle. eg 1111-1111')
							raise
					elif not letter.isnumeric() and letter != 'X':
						errors.append('Malformed ISSN. ISSN is 8 numbers with a - in the middle. eg. 1111-1111')
						raise
					
				search = ISSN.objects.get(issn=query)
				errors.append(search.journal_id)
				journal = Journal.objects.get(title=search.journal_id)
				return render(request, 'permission/details.html', {'journal': journal, 'domain_name': domain_name})
	
			except:
				errors.append('ISSN not found')
				errors.append(sys.exc_info()[0])
					
	return render(request, 'permission/search_form.html', {'errors': errors})

def BULKReplaceAgreement(request):
	if 'toReplace' in request.GET:
		toReplace = request.GET['toReplace']
	
