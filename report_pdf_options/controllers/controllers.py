from odoo import http
from odoo.addons.web.controllers.main import ReportController
import json


class PrtReportController(ReportController):
    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, context=None):
        res = super(PrtReportController, self).report_download(data, context)
        if json.loads(data)[1] in ('open', 'print'):
            res.headers['Content-Disposition'] = res.headers['Content-Disposition'].replace('attachment', 'inline')
        return res
