from django.contrib import admin

# Register your models here.
from .models import Machine, Electrometer, IonChamber, IonChamberAdditionalInfo,\
 QATestDefinition, QATestAttributeDefinition

admin.site.register(Machine)

#admin.site.register(Electrometer)

#admin.site.register(IonChamber)

class IonChamberAdditionalInfoInline(admin.TabularInline):
    model = IonChamberAdditionalInfo

@admin.register(IonChamber)
class IonChamberAdmin(admin.ModelAdmin):
	model = IonChamber

	inlines = [IonChamberAdditionalInfoInline]

class QATestAttributeDefinitionInline(admin.TabularInline):
	model = QATestAttributeDefinition

@admin.register(QATestDefinition)
class QATestDefinitionAdmin(admin.ModelAdmin):
	model = QATestDefinition
	inlines = [QATestAttributeDefinitionInline]
