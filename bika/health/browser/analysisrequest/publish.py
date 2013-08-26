from bika.lims.browser.publish import doPublish
from bika.health import bikaMessageFactory as _h
from bika.lims import bikaMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AnalysisRequestPublish(doPublish):

    template = ViewPageTemplateFile("report_results.pt")

    def __call__(self):
        self.ar = self.analysis_requests[0]
        self.patient = self.ar.Schema()['Patient'].get(self.ar)
        return super(AnalysisRequestPublish, self).__call__()

    def get_mail_subject(self, ar):
        subject, totline = doPublish.get_mail_subject(self, ar)
        client = ar.aq_parent
        subject_items = client.getEmailSubject()
        if 'health.cp' in subject_items:
            pat = ar.Schema().getField('Patient').get(ar)
            cpid = pat and pat.getClientPatientID() or None
            if cpid:
                cps_line = _h('CPID: %s') % cpid
                if totline:
                    totline += ' '
                totline += cps_line

            subject = _('Analysis results for %s') % totline

        return subject, totline
