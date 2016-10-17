from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string


def main_page(request):
    return render(request, 'index.html')


def pdf_view(request):
    if request.META['REQUEST_METHOD'] == 'GET':
        return HttpResponse(status=404)
    base_url = "http://%s/" % request.get_host()
    template_url = request.POST['template']
    force_one_page = request.POST.get('force-one-page', False)
    allowed_templates = ['report-summary.html']
    if template_url not in allowed_templates:
        raise ValueError("%s is not an allowed template" % template_url)

    html = render_to_string(template_url, {
        'STATIC_URL': 'static/',
        'content': request.POST['content']})
    rendered = HTML(string=html, base_url=base_url).render()
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
