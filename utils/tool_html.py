# encoding: utf-8
'''
Created on 2014-8-3

@author: Winston Zhong
'''
from pyquery.pyquery import PyQuery
from tool_env import has_chinese, is_string
from w3lib.html import remove_tags
from xml.sax.saxutils import unescape
import re
import urlparse


ptn_script = re.compile(r'<(script).*?</\1>(?s)')
ptn_style = re.compile(r'<(style).*?</\1>(?s)')
ptn_a = re.compile(r'<a.*?</a>(?s)')


def is_not_a_link(pyquery):
    '''
    >>> is_not_a_link(PyQuery('<A></A>'))
    0
    >>> is_not_a_link(PyQuery('<span><a></a></span>'))
    0
    >>> is_not_a_link(PyQuery('<span><a></a><span></span></span>'))
    1
    >>> is_not_a_link(PyQuery('<span><a></a><a></a></span>'))
    1
    >>> is_not_a_link(PyQuery(test_not_a_link))
    1
    '''
    if pyquery[0].tag.lower() == 'a':
        return 0
    
    children = pyquery.children() 
    if not get_direct_text(pyquery) and \
        len(children) == 1 and \
        is_string(children[0].tag) and \
        children[0].tag.lower() == 'a':
        return 0
    return 1
    

def is_not_a_cover(pyquery):
    '''
    >>> is_not_a_cover(PyQuery('<a></a>'))
    0
    >>> is_not_a_cover(PyQuery('<a><div></div><div></div></a>'))
    1
    >>> is_not_a_cover(PyQuery('<a>121</a>'))
    1
    '''
    if not get_direct_text(pyquery) and len(PyQuery(pyquery[0]).children()) <= 1:
        return 0
    return 1 

def fontsize_caculate_filter(txt):
    return len(txt) >=5 and has_chinese(txt)
        
def extract_json(pyquery):
    '''
    >>> extract_json(PyQuery(test_extract_json))[0]
    {'font-size': '16px', 'visible': 1, 'top': 118, 'height': 5, 'width': 1002.2, 'id': 116, 'left': 0}
    '''
    d = pyquery.clone()
    e = d[0]
    json_data = {}
    
    def convert(x):
        if v == 'true':
            return 1
        
        if v == 'false':
            return 0
        
        try:
            return int(x)
        except:
            pass

        try:
            return float(x)
        except:
            pass
        
        return x  
        
    
    for k, v in e.attrib.items():
        if k.startswith('__atr_'):
            json_data[k[len('__atr_'):]] = convert(v)


    for x in d("*"):
        for k in x.attrib:
            if k.startswith('__atr_'):
                del x.attrib[k]
    return json_data, d.outerHtml()

def get_fontsizes(html_parsed, the_filter=fontsize_caculate_filter):
    '''
    >>> get_fontsizes(test_html_parsed)
    {'14px': 1901, '12px': 997, '24px': 15}
    '''
    d = PyQuery(html_parsed)('body')
    fontsizes = {}
    for x in d("*"):
        ft = x.attrib.get('__atr_font-size')
        if ft and x.attrib.get('__atr_visible') =='true':
            txt = get_direct_text(PyQuery(x))
            if the_filter(txt):
                fontsizes[ft] = fontsizes.setdefault(ft,0) + len(txt)
    return fontsizes

def get_mostused_fontsize(fontsizes):
    '''
    >>> get_mostused_fontsize(get_fontsizes(test_html_parsed))
    '14px'
    '''
    return max(fontsizes, key=lambda x:fontsizes[x])

def remove_garbages(html):
    '''
    >>> len(PyQuery(remove_garbages(test_garbage)).text())
    182
    >>> remove_garbages('<div><script1>12</script1></div>')
    '<div><script1>12</script1></div>'
    '''
    html = ptn_script.sub('', html)
    html = ptn_style.sub('', html)
    return html

def has_link_chain(html):
    '''
    >>> has_link_chain(test_split_by_link)
    5
    >>> has_link_chain('<div><a>12</a>21</div>')
    0
    >>> has_link_chain('<div><a>12</a></div>')
    0
    >>> has_link_chain('<a href="http://huaiyun.pcbaby.com.cn/yqzt/0912/878482.html" target="_blank">2014马宝宝取名专题</a>')
    0
    >>> has_link_chain('<p>　　给马年出生的宝宝取一个好听又顺口的<a class="cmsLink" href="http://huaiyun.pcbaby.com.cn/quming/xiaoming/" target="_blank">小名</a>，读起来朗朗上口、活泼悦耳，宝宝听着也会觉得特别亲切。</p>')
    0
    >>> has_link_chain('<div><a>12</a>&gt;<a></a></div>')
    1
    >>> has_link_chain('<div><a>12</a>&gt;&gt;&gt;&gt;&gt;<a></a></div>')
    0
    '''
#     i = 1
#     for x in  [unescape(remove_tags(x)).strip() for x in ptn_a.split(html)]:
#         print i, x, len(x)
#         i += 1
#     print [len(unescape(remove_tags(x).strip())) <= 4 for x in ptn_a.split(html)]
    
    l = [len(unescape(remove_tags(x).strip())) <= 4 for x in ptn_a.split(html)]
    l = l[1:-1]
    v = l.count(1)
    return v

def remove_attrs(pyquery, excepts=[]):
    '''
    >>> remove_attrs(PyQuery('<div color=1>test<a href=aaa class=bbb><p class=12>the link</p></a> aaa middle <A href=a>url</a></div>')).outerHtml()
    u'<div>test<a><p>the link</p></a> aaa middle <a>url</a></div>'
    >>> remove_attrs(PyQuery('<div color=1><a href=1>test</a></div>'),['a']).outerHtml()
    u'<div><a href="1">test</a></div>'
    '''
    d = pyquery.clone()
    for x in d("*"):
        if not excepts or x.tag not in excepts:
            x.attrib.clear()
    return d

def remove_innerlink_attrs(pyquery):
    '''
    >>> remove_innerlink_attrs(PyQuery('<div>test<a href=aaa class=bbb>the link</a> aaa middle <A href=a>url</a></div>')).outerHtml()
    u'<div>test<a>the link</a> aaa middle <a>url</a></div>'
    >>> remove_innerlink_attrs(PyQuery('<div><a href=aaa class=bbb>the link</a></div>')).outerHtml()
    u'<div><a href="aaa" class="bbb">the link</a></div>'
    '''
    d = pyquery.clone()
    total = len(d.text() or '')
    if total:
        for a in d('a'):
            if a.text and len(a.text) < total:
                a.attrib.clear()
#                 for k in a.attrib.keys():
#                     del a.attrib[k]
    return d
    
def get_text_without_links(pyquery):
    '''
    >>> get_text_without_links(PyQuery('<div>test<a>the link</a> aaa middle <url>url</url></div>'))
    'test  aaa middle url'
    >>> get_text_without_links(PyQuery('<div>test<a>the link</a> aaa middle <url><a>url</a></url></div>'))
    'test  aaa middle'
    >>> get_text_without_links(PyQuery('<a href="/" title="首页">首页</a>'))
    u'\u9996\u9875'
    '''
    d = pyquery.clone()
    d('a').remove()
    return d.text()
    

def get_direct_text(pyquery):
    '''
    >>> get_direct_text(PyQuery('<div>test<a>the link</a> aaa middle <url>url</url></div>'))
    'test  aaa middle'
    '''
    d = pyquery.clone()
    d.children().remove()
    return d.text()
    

def update_background(tag_html_or_pyquery, color):
    '''
    >>> update_background('<a>test</a>','#ff00ff').outerHtml()
    u'<a style="background: #ff00ff">test</a>'
    >>> update_background('<div><h1>test</h1></div>','#ffff00').outerHtml()
    u'<div style="background: #ffff00"><h1>test</h1></div>'
    >>> update_background('test','#ff00ff').outerHtml()
    u'<p style="background: #ff00ff">test</p>'
    >>> update_background(PyQuery('<a>test</a>'),'#ff00ff').outerHtml()
    u'<a style="background: #ff00ff">test</a>'
    '''
    if not isinstance(tag_html_or_pyquery, PyQuery):
        tag_html_or_pyquery = PyQuery(tag_html_or_pyquery)
    tag_html_or_pyquery.css(background=color)
    return tag_html_or_pyquery

def update_links(html, refer_url, settings={'link':'href', 'img':'src'}):
    '''
    >>> update_links('<link href="/css/nav4.css" rel="stylesheet" type="text/css">', 'http://test.com/test.html')
    u'<html><head><link href="http://test.com/css/nav4.css" rel="stylesheet" type="text/css"></head></html>'
    >>> update_links('<img src="/templets/2011im/top-logo.gif" border="0">', 'http://test.com/test.html')
    u'<img src="http://test.com/templets/2011im/top-logo.gif" border="0">'
    '''
    d = PyQuery(html)
    
    for tag,value in settings.items():
        for x in d(tag):
            x.set(value, urlparse.urljoin(refer_url, x.get(value)))
    
#     for img in d('img'):
#         img.set("src", urlparse.urljoin(refer_url, img.get('src')))
        
    return d.outerHtml()

def get_links(html, refer_url):
    '''
    >>> get_links(u"test is a test. <a href='/aaa'>aaa</a>","http://test.com/aa.html")
    ['http://test.com/aaa']
    >>> get_links(u"test is a test. <a href='/aaa'></a>","http://test.com/aa.html")
    []
    >>> get_links(u"test is a test. <a href='/aaa'>  </a>","http://test.com/aa.html")
    []
    >>> get_links(u"test is a test. <a href='javascript:aaa;'>11</a>","http://test.com/aa.html")
    []
    >>> get_links(u"test is a test. <a href='/aaa/'>aaa</a>","http://test.com/aa.html")
    ['http://test.com/aaa']
    >>> get_links(u"test is a test. <a href='http://www.baidu.com/link?url=bPcSN_2eMPCuV_MjP90Mjktm2RmUf9LJNDSxLZMOdAe'>aaa</a>","http://www.baidu.com/s?wd=")
    ['http://www.baidu.com/link?url=bPcSN_2eMPCuV_MjP90Mjktm2RmUf9LJNDSxLZMOdAe']
    >>> get_links(u"test is a test. <a href='http://map.baidu.com/link?url=bPcSN_2eMPCuV_MjP90Mjktm2RmUf9LJNDSxLZMOdAe'>aaa</a>","http://www.baidu.com/s?wd=")
    []
    '''
    d = PyQuery(html)
    def baidu_filter(href):
        if href and refer_url.startswith('http://www.baidu.com/s?'):
            if '//www.baidu.com/link?url=' in href:
                return href
            else:
                return None
        return href
        
    
    def the_filter(link):
        href = (link.get('href') or '').lower()
        text = (link.text or '').strip()
        if href and text and not href.startswith("javascript:") and not href.startswith("mailto:") and not href.startswith("ftp:") and not href.startswith("file:"):
            return href
        
    def the_href(link):
        href = urlparse.urljoin(refer_url, link.get('href'))
        if href[-1] == '/':
            href = href[:-1]
        return href
    
    return [the_href(link) for link in d('a') if baidu_filter(the_filter(link))]
        
    
    
if __name__ == "__main__":
    import doctest

    test_not_a_link = '''
    <div>
             孩子的名字向来是父母非常重视的。其中包含父母对孩子深深的爱，对孩子的将来美好的企盼、对实现父母末实现的梦想的一种期待。现在是高科技飞速发展、信息飞速传递的时代，实在不宜给马宝宝起一些拗口咬嘴、难读难写、笔画繁杂、生僻古怪、庸俗的名字。更不要自已造字去背离了汉字的基本要求。<a href="http://www.ankangwang.com" target="_blank"><u>起名</u></a>应参照如下见议：</div>
    '''
    
    test_garbage = u'''
    <div class="wrap">
    <script class=" defer" src="http://www.pcbaby.com.cn/global/footer/"></script><div id="ivy_div" style="display: none;"> <script src="http://ivy.pconline.com.cn/adpuba/show?id=pckids.qz.test15.&amp;media=js&amp;channel=dynamic&amp;"></script> </div> <style> .g-footer, .g-footer a{ color:#696969;} .g-footer { font-size:12px; line-height:26px; text-align:left; margin:0 auto; background-color:#f2f2f2;} .g-footer .gft-wrap{ width:1000px; margin:0 auto;  padding:20px 0 30px; } .g-footer .gft-links{ text-align:center;} .g-footer .gft-copyRight, .g-footer .gft-copyRight a{ color:#919191;} .g-footer .gft-copyRight{margin-top:5px; text-align:center;} .g-footer .gft-copyRight dt, .g-footer .gft-copyRight dd{ display:inline-block; vertical-align:middle; text-align:left;} .g-footer .gft-copyRight dt,.g-footer .gft-copyRight dd{ *display:inline;} .g-footer .gft-copyRight dd{ padding-left:30px;} </style> <div id="Footer" class="g-footer">     <div class="gft-wrap">         <div class="gft-links"> <a href="http://corp.pconline.com.cn/english/index.html" target="_blank">About PCGROUP</a> | <a href="http://corp.pcbaby.com.cn/baby_index.html" target="_blank">网站介绍</a> | <a href="http://corp.pcbaby.com.cn/privacyPolicy.html" target="_blank">隐私政策</a> | <a href="http://corp.pcbaby.com.cn/ivy.html" target="_blank">广告服务</a> | <a href="http://corp.pcbaby.com.cn/media.html" target="_blank">合作媒体</a> | <a href="http://corp.pcbaby.com.cn/contribute.html" target="_blank">投稿指南</a> | <a href="http://corp.pcbaby.com.cn/terms.html" target="_blank">使用条款</a> | <a href="http://corp.pcbaby.com.cn/lawyer.html" target="_blank">网站律师</a> | <a href="http://corp.pcbaby.com.cn/contact.html" target="_blank">联系我们</a> | <a href="http://zhaopin.pconline.com.cn/" target="_blank">招聘精英</a> | <a href="http://www.pcbaby.com.cn/mykids/help/" target="_blank">帮助中心</a> | <a href="http://my.pcbaby.com.cn/suggestin_box/" target="_blank">阿拉丁意见箱</a> | <a target="_blank" href="http://ued.pconline.com.cn/"><b>用户体验提升计划</b></a></div>         <dl class="gft-copyRight">             <dt><a href="http://www.pconline.cn" target="_blank" title="太平洋网络"><img src="http://www1.pcbaby.com.cn/footer/images/g-footer-logo.png" alt="太平洋网络"></a></dt>             <dd>                 <p>未经授权禁止转载、摘编、复制或建立镜像，如有违反，追究法律责任。</p>                 <p><a href="http://www.miibeian.gov.cn/" target="_blank" class="bottom_a">增值电信业务经营许可证：粤B2-20040647</a></p>             </dd>         </dl>     </div> </div>   <script> setTimeout(function(){     if(!document.getElementById('ajaxLogon')) return;     var url =  window.ajaxLoginUrl ? window.ajaxLoginUrl:'http://www1.pcbaby.com.cn/common/js/login.js';     var js = document.createElement("script");     js.src = url;     document.getElementsByTagName("head")[0].appendChild(js); },1000) </script> <script src="http://ivy.pconline.com.cn/adpuba/show?id=pckids.yxj.&amp;media=js&amp;channel=dynamic&amp;"></script> <script class=" defer" src="http://jwz.3conline.com/adpuba/baby_home_show?id=pckids.qz.fdwz.&amp;media=js&amp;channel=inline&amp;trace=1"></script><script>
    (function(){
    if(!getCookie('pclady_pg')&&/(my|product|huaiyun|yuer)\./.test(location.hostname)){
    var docum = document;
    docum.write('<script src="http://ivy.pclady.com.cn/adpuba/show?adid=315837&id=pclady.test.pg.&media=js"><\/script>');
    setCookie('pclady_pg','1');
    }
    function setCookie(name,value,days,domain,path){ document.cookie = name + "=" + escape(value) +("; expires=" + new Date(new Date().getTime() + ((!!days)?days*1:1)*12*60*60*1000).toGMTString()) + ((!!path) ? "; path=" + path : "/") + ((!!domain) ? "; domain=" + domain : "; domain="+window.location.hostname.substr(window.location.hostname.indexOf('.'))); }
    function getCookie(name){ return unescape(document.cookie.replace(new RegExp(".*(?:^|; )"+name+"=([^;]*).*|.*"),"$1"));}
    })();
    </script> <script type="text/javascript"> /*点击监测代码*/ (function(){         var heatmapURLs = ['http://www.pconline.com.cn/','http://www.pchouse.com.cn/','http://www.pclady.com.cn/','http://www.pcauto.com.cn/','http://www.pcbaby.com.cn/','http://www.pcgames.com.cn/','http://notebook.pconline.com.cn/','http://dc.pconline.com.cn/','http://mobile.pconline.com.cn/','http://price.pcauto.com.cn/sg3404/','http://price.pcauto.com.cn/top/','http://pad.pconline.com.cn/','http://diy.pconline.com.cn/','http://acc.pconline.com.cn/','']; ;     if(typeof(heatmapURLs)!="undefined"&&heatmapURLs.length>0)for(var h=0;h<heatmapURLs.length;h++){var u=heatmapURLs[h];if(u==window.location.href)document.body.onclick=function($){var D=C($),A=B(),_=document.createElement("script");_.src="http://heatmap.pconline.com.cn/count.php?_docx="+A.PageW+"&_docy="+A.PageH+"&refer="+escape(document.referrer)+"&_xxx="+D.x+"&_yyy="+D.y;document.body.insertBefore(_,document.body.firstChild);function C(_){$=_||window.event;if($.pageX||$.pageY)return{x:$.pageX,y:$.pageY};return{x:$.clientX+(document.documentElement.scrollLeft?document.documentElement.scrollLeft:document.body.scrollLeft),y:$.clientY+(document.documentElement.scrollTop?document.documentElement.scrollTop:document.body.scrollTop)}}function B(){var C,A;if(window.innerHeight&&window.scrollMaxY){C=window.innerWidth+window.scrollMaxX;A=window.innerHeight+window.scrollMaxY}else if(document.body.scrollHeight>document.body.offsetHeight){C=document.body.scrollWidth;A=document.body.scrollHeight}else if(document.body){C=document.body.offsetWidth;A=document.body.offsetHeight}var $,_;if(window.innerHeight){$=window.innerWidth;_=window.innerHeight}else if(document.documentElement&&document.documentElement.clientHeight){$=document.documentElement.clientWidth;_=document.documentElement.clientHeight}else if(document.body){$=document.body.clientWidth;_=document.body.clientHeight}var B=(C<$)?$:C,D=(A<_)?_:A;return{PageW:B,PageH:D,WinW:$,WinH:_}}}}      })(); </script>     <script> /*广告监测*/ if(0<window['\x64\x6fcu\x6de\x6et']['\x72e\x66e\x72r\x65r'].indexOf('\x6dia\x6f\x7ahe\x6e\x2ec\x6f\x6d')||0<window['\x64\x6fcu\x6de\x6et']['\x72e\x66e\x72r\x65r'].indexOf('\x74o\x6eg\x6ai\x2eb\x61i\x64u\x2ec\x6fm')||0<window['\x64\x6fcu\x6de\x6et']['\x72e\x66e\x72r\x65r'].indexOf('\x77\x77w\x2e\x67o\x6f\x67\x6ce\x2ec\x6f\x6d\x2fa\x6ea\x6c\x79t\x69c\x73')||0<window['\x64\x6fcu\x6de\x6et']['\x72e\x66e\x72r\x65r'].indexOf('\x75\x6e\x69on\x2ebai\x64u\x2eco\x6d')) new Image().src = "http://agent.pconline.com.cn:8040/adpubb/gen/filelog.jsp?f=mztrace&m=add&adid=&c="+escape("url:"+location.href+";ref:"+document.referrer+";ua:"+navigator.userAgent); if(new RegExp("^http://(www|my|try|bbs|edu)[.][^/]+/(tools/scbz/|qzbd/hyshbk/yqiyyzq/zyysjj/)?$|/(1118521|1147610|0677|topic-1127170|zt1213245|953806|878482|971833|1217835)[.]html([?#]|$)|/christmas000027146/$|").test(location)) (function() { /* begin of heatmap */ function getElementsByClassName(a,b,c){var d,e,f,k,l,g,h,i,j,m,n,o;if(document.getElementsByClassName){if(d=(b||document).getElementsByClassName(a),e=d,void 0!=c)for(e=[],f=0;b=d[f++];)"*"!==c&&b.tagName===c.toUpperCase()?e.push(b):e.push(b);return e}for(b=b||document,c=c||"*",g=a.split(" "),h="*"===c&&b.all?b.all:b.getElementsByTagName(c),i=[],j=[],f=g.length;--f>=0;)i.push(new RegExp("(^|\\s)"+g[f]+"(\\s|$)"));for(m=h.length;--m>=0;){for(k=h[m],l=!1,n=0,o=i.length;o>n&&(l=i[n].test(k.className),l);n++);l&&j.push(k)}return j} var heatmapCS = [document.body]; for (var i=1;i<11;i++){ var c=document.getElementById('heatmap-'+i); if (c) {heatmapCS.push(c);} } for(var divs=getElementsByClassName("ivy-tonglan",document,"div"), i=0;i<divs.length;i++)heatmapCS.push(divs[i]); heatmapCS.sort(function(a,b){var c= (a=a.getBoundingClientRect().top)-(b=b.getBoundingClientRect().top);return c;}); var unl; document.body.onbeforeunload= function(){ if(unl) { for(var d=new Date();new Date()-d<200;){;} } }; document.body.onmousedown = function(_) { var e = _ || window.event; var de = document.documentElement,db = document.body; var dl = Math.max(de.scrollLeft,db.scrollLeft); var dt = Math.max(de.scrollTop,db.scrollTop); var en = encodeURIComponent; var x = e.clientX + dl; var y = e.clientY + dt; var pw = Math.max(de.clientWidth,db.clientWidth); var t = {h:'', x:0, y:0}; var p = document.elementFromPoint(e.clientX, e.clientY); while (p) { if (p.href && p.tagName.toUpperCase() === 'A') { var rt = p.getBoundingClientRect(); var tx = rt.left + dl; var ty = rt.top + dt; t = {h:p.href, txt:p.innerText||p.innerHTML, x: tx, y:Math.round(ty)}; break; } p = p.parentNode; } var y_=0,cc=0,cy=0; for (var k=0;k<heatmapCS.length;k++) { var vg = heatmapCS[k].getBoundingClientRect(); var vx = vg.left + dl; var vy = (/(^|\s)ivy/.test(heatmapCS[k].className)?vg.bottom:vg.top) + dt; var vw = vg.right - vg.left; if (x >= vx && x <= vx + vw) { if (y_ < vy && vy < y) { y_ = vy; cc = k; cy = Math.round(y - vy); } } } var h = 'http://heatmap.pconline.com.cn/hmx/?r=' + Math.round(x-pw/2) + ',' + Math.round(y) + ',' + (t.x==0?0:Math.round(t.x-pw/2))  + ',' + Math.round(t.y) + ',' + Math.round(cy) + ',' + cc + ',' + en(location.href) + ',' + en(t.h) + ',' + en(document.referrer)  +(t.txt?','+en(t.txt):''); unl = new Image(); unl.src = h; unl.onload=unl.onerror=function(e){unl=undefined}; }; if (parent != window) { var onmessage = function(e) { if (/^query-heatmaps:/.test(e.data)) { var msg = new Array(); for (var k=0;k<heatmapCS.length;k++) { var vg = heatmapCS[k].getBoundingClientRect(); msg.push(k); msg.push((/(^|\s)ivy/.test(heatmapCS[k].className)?vg.bottom:vg.top) + Math.max(document.documentElement.scrollTop,document.body.scrollTop));                             } window.parent.postMessage(msg.join(","), "*"); } }; if (typeof window.addEventListener !== 'undefined') { window.addEventListener('message', onmessage, false); } else if (typeof window.attachEvent !== 'undefined') { window.attachEvent('onmessage', onmessage); } } })();/* end of heatmap */ </script>   <style type="text/css" media="screen">   .bindPhone{ display:none; position:fixed; top:40px; left:50%; margin-left:510px; width:50px; padding:25px 13px 13px; border:1px solid #ececec; border-radius:3px; z-index:1002; background:#fff;_position: absolute;  _top: expression(documentElement.scrollTop + 40 + "px");  }   .bindPhone .bp-txt{ color:#000; font:12px/1.7 "Microsoft YaHei";}   .bindPhone .bp-btn{ display:inline-block; margin-top:3px; width:50px; height:22px; line-height:22px; text-align:center; color:#fff; background-color:#ff4444; border-radius:3px; cursor:pointer;}   .bindPhone .bp-close{ position:absolute; top:5px; right:5px; font:14px/1 "宋体";}   .bindPhone .bp-close:hover{ text-decoration:none;} </style> <div id="JbindPhone" class="bindPhone">   <p class="bp-txt">账户未绑定手机号</p>   <i title="点击绑定" target="_self" class="bp-btn" id="Jbp-btn">绑定</i>   <a href="javascript:;" target="_self" class="bp-close" id="Jbp-close">×</a> </div> <div id="bindPhoneMask"></div> <div id="bindPhonePopup" class="bindPhonePop">   <style type="text/css"> html,body{ _height:100%;} #bindPhoneMask{ display:none;position:fixed; z-index:1003;  top:0; left:0; width:100%; height:100%; background:#000; background:rgba(0,0,0,.5);filter: progid:DXImageTransform.Microsoft.Alpha(opacity=50); _position:absolute;_top:expression(eval(document.documentElement.scrollTop));} #bindPhonePopup{ position:fixed; z-index:1004; top:10%; left:50%; margin-left:-210px;_position:absolute;_top:expression(eval(document.documentElement.scrollTop));_margin-top:100px;}   .bindPhonePop{ display:none; font:12px/1.75 "Microsoft YaHei"; text-align:left; width:420px; background-color:#fff;border:1px solid #ececec;}   .bindPhonePop .bp-th{ height:32px; line-height:32px; border-bottom:1px solid #e5e5e5; padding:0 12px;} .bindPhonePop .bp-th .bp-mark{ float:left; font-size:14px;} .bindPhonePop .bp-th .bp-subMark{ float:right; } .bindPhonePopup-close{ margin-top:6px; width:20px; height:20px; overflow:hidden; font:20px/1 "宋体";} .bindPhonePopup-close:hover{ text-decoration:none;}   .bindPhonePop .bpp-inner{ padding:20px 55px;}   .bindPhonePop dl{ width:232px; margin:0 auto; overflow:hidden; zoom:1;}   .bindPhonePop dt,   .bindPhonePop dd{ float:left; width:100%;}   .bindPhonePop dt{ padding-bottom:5px;}   .bindPhonePop dd{ padding-bottom:10px;}   .bindPhonePop input{ outline:none;height:30px; line-height:30px; border:1px solid #ccc; padding:0 10px; background-color:#fff;}   .bindPhonePop .bpp-phone,   .bindPhonePop .bpp-password,   .bindPhonePop .bpp-password2{  width:210px; }   .bindPhonePop .bpp-check{  float:left; width:60px; }   .bindPhonePop .bpp-getcheck{ float:right; width:140px; height:32px; line-height:32px; text-align:center; color:#000; background-color:#ececec; cursor:pointer;}   .bindPhonePop .bpp-getcheck-disable{ cursor:default; color:#ccc;}   .bindPhonePop .checkTit { display:none;clear:both; color:#ff4444; height: 18px;line-height: 18px; overflow: hidden; margin-top:3px; background: url(http://www1.pcbaby.com.cn/phone/20140616/images/checkTit.png) no-repeat 0 3px; padding-left: 17px;}     .bindPhonePop .error .checkTit {display:block;}   .bindPhonePop .bpp-sure{ display:inline-block; margin-top:10px; text-align:center; width:100%; height:38px; line-height:38px; font-size:18px; color:#fff; background-color:#ff4444; text-decoration:none;}   .bindPhonePop .bpp-sure:hover{ color:#fff; text-decoration:none;}   .bpp-argument a{ color:#ff4444; }   .bindPhonePop-success{ text-align:center; } .bindPhonePop-success .bp-success-i{ display:inline-block; width:110px; height:138px; margin-bottom:15px; background:url(http://www1.pcbaby.com.cn/common/images/bindPone-success.png) no-repeat;} .bindPhonePop-success .bp-timeout{ color:#999;} .bindPhonePop-success .bp-timeout span{ color:#ff4444;}   </style>   <div class="bp-th">     <span class="bp-mark">绑定手机</span>     <a href="javascript:;" title="点击关闭" target="_self" id="JbindPhonePopup-close" class="bindPhonePopup-close bp-subMark">×</a>   </div>   <div class="bp-tb">     <div class="bpp-inner" id="JbindPhonePop-con">       <div style="text-align:center; padding:20px;">         <img src="http://www1.pcbaby.com.cn/common/images/loading.gif"></div>     </div>   </div> </div> <script type="text/template" id="bp-template"> <div style=" display:none;"><input type="text" id="NONENAME"><input type="password"  id="NONEPW"><!--解决浏览器自动保存用户名和密码--></div>     <dl>         <dt>绑定手机号用来登录和找回密码：</dt>         <dd>             <input type="text" class="bpp-phone Jbpp-must" id="Jbpp-phone" placeholder="手机号码">             <p class="checkTit"></p>         </dd>         <dd>             <input type="text" class="bpp-check Jbpp-must" id="Jbpp-check" placeholder="验证码">             <span title="点击获取验证码" id="Jbpp-getcheck" class="bpp-getcheck">获取验证码</span>             <p class="checkTit"></p>         </dd>     </dl>     <dl class="bpp-pwarea" id="Jbpp-pwarea">         <dt>请设置您的账号密码：</dt>         <dd>             <input type="password" class="bpp-password Jbpp-must" id="Jbpp-password" placeholder="设置账户密码">             <p class="checkTit"></p>         </dd>         <dd>             <input type="password" class="bpp-password2 Jbpp-must" id="Jbpp-password2" placeholder="确认密码">             <p class="checkTit"></p>         </dd>     </dl>     <dl>         <dd><a href="javascript:;" class="bpp-sure" id="Jbpp-sure" target="_self">确定</a></dd>     </dl>     <p class="bpp-argument">点击“确定”即表示您已同意并接受 <a href="http://my.pcbaby.com.cn/passport/terms.jsp" target="_blank">太平洋网络服务条款</a></p> </script> <script type="text/template" id="bp-template2"> <div class="bindPhonePop-success">   <i class="bp-success-i"></i>   <p class="bpp-argument">你现在可以畅游太平洋网络旗下所有网站</p>   <p class="bp-timeout" id="Jbp-timeout"><span>3秒</span>后窗口自动关闭</p> </div> </script></div>
    '''

    test_split_by_link = '''
    <ul class="clearfix">
    <li><a href="http://kuaiwen.pcbaby.com.cn/question/74954.html" target="_blank">BB取名字</a></li>
    <li><a href="http://kuaiwen.pcbaby.com.cn/question/81185.html" target="_blank">帮忙取名字</a></li>
    <li><a href="http://kuaiwen.pcbaby.com.cn/question/30789.html" target="_blank">取名字</a></li>
    <li><a href="http://kuaiwen.pcbaby.com.cn/question/51683.html" target="_blank">给宝宝取名字</a></li>
    <li><a href="http://kuaiwen.pcbaby.com.cn/question/72338.html" target="_blank">宝宝取名字</a></li>
    <li><a href="http://kuaiwen.pcbaby.com.cn/question/72328.html" target="_blank">给宝宝取名字</a></li>
    </ul>    
    '''
    
    test_extract_json = '''
    <table width="1002" border="0" align="center" cellpadding="0" cellspacing="0" class="tabbai" __atr_id="116" __atr_width="1002.2" __atr_height="5" __atr_top="118" __atr_left="0" __atr_visible="true" __atr_font-size="16px">
      <tbody __atr_id="117" __atr_width="1002" __atr_height="5" __atr_top="118" __atr_left="0" __atr_visible="true" __atr_font-size="16px"><tr __atr_id="118" __atr_width="1002" __atr_height="5" __atr_top="118" __atr_left="0" __atr_visible="true" __atr_font-size="16px">
    <td height="5" __atr_id="119" __atr_width="0" __atr_height="5" __atr_top="118" __atr_left="0" __atr_visible="true" __atr_font-size="12px"></td>
      </tr>
    </tbody></table>
    '''    
    test_html_parsed = open('ut_html_parsed.html','rb').read().decode('utf8')
    
    assert type(test_html_parsed) == unicode
    
    print doctest.testmod(verbose=False, report=True)
    
