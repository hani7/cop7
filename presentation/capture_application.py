"""Capture actual application screens through Chrome DevTools, using demo accounts."""
from pathlib import Path
import urllib.request
import json
import base64
import time
import sys
import websocket

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'presentation/captures'
OUT.mkdir(exist_ok=True)
BASE='http://127.0.0.1:5179'
pages=json.load(urllib.request.urlopen('http://127.0.0.1:9231/json'))
ws=websocket.create_connection(next(p['webSocketDebuggerUrl'] for p in pages if p['type']=='page'), origin='http://localhost:9231',timeout=30)
serial=0
def cmd(method, params=None):
    global serial
    serial+=1
    ws.send(json.dumps({'id':serial,'method':method,'params':params or {}}))
    while True:
        result=json.loads(ws.recv())
        if result.get('id')==serial:
            if 'error' in result: raise RuntimeError(result['error'])
            return result.get('result',{})
def js(expression):
    r=cmd('Runtime.evaluate',{'expression':expression,'awaitPromise':True,'returnByValue':True})
    if 'exceptionDetails' in r: raise RuntimeError(r['exceptionDetails'])
    return r.get('result',{}).get('value')
def wait(expression, timeout=20):
    until=time.monotonic()+timeout
    while time.monotonic()<until:
        if js('Boolean('+expression+')'): return
        time.sleep(.2)
    raise RuntimeError('Timeout: '+expression+'\n'+str(js('document.body.innerText')).split('Identifiant')[0][:1200])
def settle():
    wait("!document.querySelector('.loading-bar,.boot')")
    js('document.fonts.ready.then(()=>true)')
    time.sleep(.3)
def click(label, selector='button'):
    expression=f"[...document.querySelectorAll({json.dumps(selector)})].find(e=>e.textContent.trim()==={json.dumps(label)} || e.getAttribute('aria-label')==={json.dumps(label)} || e.querySelector('span')?.textContent.trim()==={json.dumps(label)})"
    wait(expression)
    js(f"({expression}).click()")
    settle()
def navigate(page):
    click(page,'.topnav button, .settings-subnav button, .technician-bottom-nav button')
    settle()
def viewport(w=1600,h=1000):
    cmd('Emulation.setDeviceMetricsOverride',{'width':w,'height':h,'deviceScaleFactor':1.5,'mobile':False})
def capture(name, selector=None):
    settle()
    assert not js("!!document.querySelector('.alert.error')"), js("document.querySelector('.alert.error')?.textContent")
    params={'format':'png','captureBeyondViewport':True}
    params['clip']=js('({x:scrollX,y:scrollY,width:innerWidth,height:innerHeight,scale:1})')
    if selector:
        js(f"document.querySelector({json.dumps(selector)}).scrollIntoView({{block:'center'}})")
        time.sleep(.25)
        box=js(f"(()=>{{const r=document.querySelector({json.dumps(selector)}).getBoundingClientRect();return {{x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height,scale:1}}}})()")
        params['clip']=box
    image=cmd('Page.captureScreenshot',params)
    (OUT/(name+'.png')).write_bytes(base64.b64decode(image['data']))
    print('CAPTURED '+name,flush=True)
def login(user,path='/'):
    cmd('Network.clearBrowserCookies')
    cmd('Page.navigate',{'url':BASE+path})
    wait("!!document.querySelector('.login')")
    creds=json.loads((ROOT/'.runtime/presentation-demo/access.json').read_text())
    for selector,value in [('input[autocomplete=username]',user),('input[type=password]',creds['password'])]:
        js(f"(()=>{{const e=document.querySelector({json.dumps(selector)});Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,{json.dumps(value)});e.dispatchEvent(new Event('input',{{bubbles:true}}));}})()")
    click('Se connecter')
    wait("!!document.querySelector('.app-shell')")
    settle()

cmd('Page.enable'); cmd('Network.enable'); viewport()
mode=sys.argv[1] if len(sys.argv)>1 else 'all'
if mode in ['all','admin']:
    cmd('Network.clearBrowserCookies');cmd('Page.navigate',{'url':BASE})
    wait("!!document.querySelector('.login')");capture('01-connexion')
    login('demo-admin')
    js("""(async()=>{const session=await (await fetch('/api/auth/session/')).json();const list=await (await fetch('/api/users/')).json();const u=list.results.find(u=>u.username==='demo-tech');if(!u.experience.startsWith('<!--copetrolite-experience:v1-->')){const response=await fetch('/api/users/'+u.id+'/',{method:'PATCH',headers:{'Content-Type':'application/json','X-CSRFToken':session.csrfToken},body:JSON.stringify({experience:'<!--copetrolite-experience:v1-->'+u.experience})});if(!response.ok)throw new Error('Demo profile update failed');}return true;})()""")
    cmd('Page.reload');wait("!!document.querySelector('.app-shell')");settle()
    navigate('Vue d’ensemble');capture('02-tableau-bord-admin')
    navigate('Clients');capture('03-clients')
    navigate('Paramètres');navigate('Équipe');capture('04-equipe','.panel')
    navigate('Techniciens')
    click('Voir le profil complet de AMINE DEMONSTRATION')
    viewport(1440,1150);capture('05-profil-technicien','dialog')
    click('Fermer');viewport(1440,1100)
    click('Modifier AMINE DEMONSTRATION')
    click('Extraire l’expérience du CV enregistré')
    wait("!!document.querySelector('.cv-preview textarea')")
    capture('06-extraction-experience','.cv-preview')
    click('Utiliser la photo du CV')
    wait("!!document.querySelector('.technician-photo-preview') && [...document.querySelectorAll('.cv-selected-status')].some(e=>e.textContent.includes('Photo extraite'))")
    capture('07-photo-extraite','.technician-photo')
    click('Fermer');viewport()
    navigate('Projets');click('Acc?s client')
    capture('08-acces-client','dialog');click('Fermer')
    navigate('Facturation');click('Consulter');capture('09-facture','dialog');click('Fermer')
    navigate('Paiements');capture('10-paiements-client','.panel')
if mode in ['all','roles']:
    viewport();login('demo-superviseur');navigate('Projets');capture('11-projets-superviseur','.panel')
    login('demo-client','/project/login');navigate('Pointages');capture('12-validation-client','.panel')
    login('demo-tech','/tech/login');viewport(430,900);navigate('Accueil');capture('13-technicien-mobile')
    click('Saisir mes heures');capture('14-pointage-mobile');click('Fermer')
    navigate('Paiements');capture('15-gains-technicien')
ws.close()
