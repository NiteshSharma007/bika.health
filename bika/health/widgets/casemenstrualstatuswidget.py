from AccessControl import ClassSecurityInfo
from Products.ATExtensions.widget import RecordsWidget as ATRecordsWidget
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.utils import getToolByName
from bika.health.config import MENSTRUAL_STATUSES
import json


class CaseMenstrualStatusWidget(ATRecordsWidget):
    security = ClassSecurityInfo()
    _properties = ATRecordsWidget._properties.copy()
    _properties.update({
        'macro': "bika_health_widgets/casemenstrualstatuswidget",
        'helper_js': ("bika_health_widgets/casemenstrualstatuswidget.js",
                      "bika_health_widgets/patientmenstrualstatuswidget.js"),
        'helper_css': ("bika_health_widgets/casemenstrualstatuswidget.css",),
    })

    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        outvalues = []
        values = form.get(field.getName(), empty_marker)
        for value in values:
            outvalues.append({'FirstDayOfLastMenses': value.get('FirstDayOfLastMenses', ''),
                              'MenstrualCycleType': value.get('MenstrualCycleType', ''),
                              'Pregnant': bool(value.get('Pregnant', False)),
                              'MonthOfPregnancy': value.get('MonthOfPregnancy', '')})

        # Save patient's MenstrualStatus
        if 'PatientID' in form:
            bpc = getToolByName(instance, 'bika_patient_catalog')
            patient = bpc(portal_type='Patient', id=form['PatientID'])
            if patient and len(patient)>0:
                patient = patient[0].getObject()
                patient.setMenstrualStatus([{'Hysterectomy': bool(values[0].get('Hysterectomy', False)),
                                             'HysterectomyYear': values[0].get('HysterectomyYear', ''),
                                             'OvariesRemoved': bool(values[0].get('OvariesRemoved', False)),
                                             'OvariesRemovedYear': values[0].get('OvariesRemovedYear', '')
                                             }]);

        return outvalues, {}

    def jsondumps(self, val):
        return json.dumps(val)

    def getMenstrualStatusesList(self):
        statuses = {}
        for key in MENSTRUAL_STATUSES.keys():
            statuses[key] = MENSTRUAL_STATUSES.getValue(key)
        return statuses

    def getPatientsGender(self):
        gender = 'dk'
        patientid = self.aq_parent.getPatientID()
        if patientid:
            bpc = getToolByName(self, 'bika_patient_catalog')
            patient = bpc(portal_type='Patient', id=patientid)
            gender = len(patient) > 0 \
                        and patient[0].getObject().getGender() or 'dk'
        return gender

    def getMenstrualStatus(self):

        statuses = {'FirstDayOfLastMenses':'',
                     'MenstrualCycleType': MENSTRUAL_STATUSES.keys()[0],
                     'Pregnant':False,
                     'MonthOfPregnancy':0,
                     'Hysterectomy': False,
                     'HysterectomyYear': '',
                     'OvariesRemoved': False,
                     'OvariesRemovedYear': ''}

        # Fill with patient's Menstrual status info
        bpc = getToolByName(self, 'bika_patient_catalog')
        patientid = self.aq_parent.getPatientID()
        if patientid:
            patient = bpc(portal_type='Patient', id=patientid)
            if len(patient) > 0:
                patient = patient[0].getObject()
                pms = patient.getMenstrualStatus()
                if pms and len(pms) > 0:
                    value = pms[0]
                    statuses = dict(statuses.items() + value.items())

        if len(self.aq_parent.getMenstrualStatus()) > 0:
            cms = self.aq_parent.getMenstrualStatus()
            if cms and len(cms) > 0:
                value = cms[0]
                statuses = dict(statuses.items() + value.items())

        return [statuses]

registerWidget(CaseMenstrualStatusWidget,
               title='CaseMenstrualStatusWidget',
               description='Menstrual status information',
               )