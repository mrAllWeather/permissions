from django.forms import CharField
from django.core import validators

class Search(forms.Form):
	issn = forms.CharField()

class ISSNField(CharField):
	def validate(self, value):
		if(value.length != 8):
			raise forms.ValidationError("An ISSN has only 9 characters (EG. 1221-1232)")
		else:
			for i, letter in enumerate(value):
				if(i==4):
					if letter != '-':
						raise forms.ValidationError("An ISSN has 8 digits with a dash in the middle (eg. 1221-1232)") 
					
				else:
					if not letter.isnumeric() and letter != 'X':

					else:
						raise forms.ValidationError("An ISSN has 8 digits with a dash in the middle (eg. 1221-1232)")
	
				
