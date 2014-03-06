from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from permission.models import Journal, ISSN, Publisher, Agreement

# Admin Functions

# Admin Views
class ISSNInline(admin.TabularInline):
	model = ISSN
	extra = 1

class PublisherAdmin(admin.ModelAdmin):
	list_display = ('name', 'website')
	search_fields = ['journal__title',]

class JournalAdmin(admin.ModelAdmin):
	inlines = [ISSNInline]
	list_display = ('title', 'publisher', 'agreement')
	search_fields = ['issn__issn', 'title', 'agreement__evidence_location']
	list_filter = ['publisher', ]

class AgreementAdmin(admin.ModelAdmin):
	list_display = ('__unicode__', 'journal_only', 'publisher', 'last_verified')
	search_fields = ['publisher__name', 'journal__title']
	list_filter = ['publisher', ]

	def BULKReplaceAgreement(self, request, queryset):
		toReplace = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
		return render(request, 'permission/BULKReplaceAgreement.html', {'toReplace': toReplace})
		
		
	
# Register your models here.
admin.site.register(Journal, JournalAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Agreement, AgreementAdmin)
