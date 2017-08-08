from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pyquery.pyquery import PyQuery

from collection.models import TitleEntity, NameEntity, HtmlContent


# Create your views here.
def test2(request):
    return HttpResponse('ok')

def set_background_color(d, eid, color="FFFF00"):
#     print eid
    if eid:
        x = d('[jbid="%s"]' % eid)
        x.attr['style'] = x.attr['style'] or '' + "background-color:#%s;" % color

def get_html(te, color="FFFF00"):
    d = PyQuery(te.html.html)
#     x = d('[jbid="%d"]' % te.eid)
#     x.attr['style'] = x.attr['style'] or '' + "background-color:#FFFF00;"
    set_background_color(d, te.eid, color)
    
    d('iframe').remove()
    return d.html()

def TitleEntityView(request, tid):
    return HttpResponse(get_html(TitleEntity.objects.get(id=tid), "FF0000")) 

def NameEntityView(request, tid):
    return HttpResponse(get_html(NameEntity.objects.get(id=tid)))


@csrf_exempt
def NameEntityAPI(request):
    if request.method == "POST":
        hc = HtmlContent.objects.get(id=request.POST.get('hid'))
        NameEntity.objects.update_or_create(html=hc, 
                                              eid=request.POST.get('nid'),
                                              defaults = {
                                                  "trainee":1,
                                                  "label": request.POST.get('label')
                                                          }
                                              )
        return HttpResponse('ok')

def HtmlContentView(request, tid):
    NameEntity.reload_model()
    hc = HtmlContent.objects.get(id=tid)

    d = PyQuery(hc.html)
    
    set_background_color(d, hc.title_id, color="FF0000")
    
    name_ids = hc.name_ids 
    print name_ids
    
    for x in name_ids:
        set_background_color(d, x, color="FFFF00")
    
    d('iframe').remove()

#     return HttpResponse(d.html())


    return render(request, 'hc.html', 
                  {
            'body':d.html(),
            'hid':hc.id,
                   },
                  )    


