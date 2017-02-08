from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test, login_required
from weasyprint import HTML
from django.template.loader import render_to_string
from datetime import datetime
from weebl.__init__ import __version__
from weebl.__init__ import __api_version__
from base64 import b64encode
from lxml import etree
from oilserver import models


def admin_check(user):
    return user.is_superuser


def main_page(request):
    return render(request, 'index.html', {
        'TMYear': datetime.now().year,
        'version': __version__,
        'api_version': __api_version__})


@user_passes_test(admin_check)
@require_http_methods(["GET"])
def refresh_views(request):
    models.BugReportView.objects.refresh()
    models.PipelineReportView.objects.refresh()
    models.ServiceReportView.objects.refresh()
    models.TestReportView.objects.refresh()
    return HttpResponse('')


@login_required(login_url='/login/ubuntu')
@require_http_methods(["GET", "POST"])
def pdf_view(request):
    if request.META['REQUEST_METHOD'] == 'GET':
        return HttpResponse(status=404)
    base_url = "http://%s/" % request.get_host()
    template_url = request.POST['template']
    force_one_page = request.POST.get('force-one-page', False)
    allowed_templates = ['report-summary.html']
    if template_url not in allowed_templates:
        raise ValueError("%s is not an allowed template" % template_url)

    def svg_embed(html):
        """For the child of nvd3 nodes (svg) munge them into b64encoded data
        as a workaround for https://github.com/Kozea/WeasyPrint/issues/75"""
        root = html.root_element
        svgs = root.findall('.//nvd3')
        for svg in svgs:
            child = svg.getchildren()[0]
            encoded = b64encode(etree.tostring(child)).decode()
            encoded_data = "data:image/svg+xml;charset=utf-8;base64," + encoded
            encoded_child = etree.fromstring('<img src="%s"/>' % encoded_data)
            svg.replace(child, encoded_child)
        return html

    html = render_to_string(template_url, {
        'STATIC_URL': 'static/',
        'content': request.POST['content']})
    rendered = svg_embed(HTML(string=html, base_url=base_url)).render()
    if force_one_page and len(rendered.pages) > 1:
        rendered = rendered.copy([rendered.pages[1]])
    pdf_file = rendered.write_pdf()
    http_response = HttpResponse(pdf_file, content_type='application/pdf')
    http_response['Content-Disposition'] = \
        'filename="%s"' % request.POST['filename']
    return http_response


def logout_view(request):
    logout(request)
    return redirect('/')
