// Tlamatini chat-avatar engine - extracted from agent_page.html (2026-07-17).
(function(){
  "use strict";
  function ready(fn){ if(document.readyState!=='loading'){setTimeout(fn,0);} else {document.addEventListener('DOMContentLoaded',fn);} }
  var FEMALE_RE=/(female|femenin|mujer|zira|jenny|aria|michelle|clara|nanami|sara|hazel|heera|catherine|hedda|elsa|paulina|helena|laura|isabel|sabina|dalia|renata|ximena|esperanza|angelica|angélica|camila|valentina|marisol|carmen|lupe|larissa|woman|girl|monica|mónica|google us english|google uk english female|google español|samantha|victoria|karen|tessa|fiona|moira|serena|allison|ava|susan|zoe|nora|mia|jess|tara|leah)/i;
  var MALE_RE=/(\bmale\b|david|mark|guy|ryan|george|james|richard|paul|thomas|daniel|alex|fred|diego|jorge|pablo|raul|raúl|gerardo|césar|cesar|luciano|mateo|andrés|andres|liberto|\bman\b|\bboy\b)/i;
  function allVoices(){ try{return window.speechSynthesis.getVoices()||[];}catch(e){return [];} }
  // ESPANOL LATINO MEXICANO PRIMERO (Angela, 2026-07-29).
  // This is the Spanish edition: every line Tlamatini speaks is Spanish. The
  // old ladder filtered voices with /^en/ ONLY, so she read Spanish sentences
  // with an English mouth ("¿Qué onda?" pronounced as English). Order now:
  // es-MX -> any Latin-American Spanish -> any Spanish -> English last resort.
  function spanishPool(){
    var vs=allVoices();
    function by(re){ return vs.filter(function(v){ return re.test(v.lang||''); }); }
    var mx=by(/^es[-_]MX/i);                     if(mx.length) return mx;
    var latam=by(/^es[-_](419|US|CO|AR|CL|PE|VE|EC|GT|CR|UY|PY|BO|DO|HN|NI|PA|SV|PR)/i);
    if(latam.length) return latam;
    // El latinoamericano es el que se busca primero, pero si no hay, el
    // castellano de Espana SI sirve (Angela, 2026-08-19): se entiende
    // perfecto. Lo que NO existe es un escalon en ingles.
    var es=by(/^es(-|_|$)/i);                    if(es.length) return es;
    // ⛔ NO HAY ESCALON EN INGLES. Aqui decia:
    //       var en=by(/^en(-|_|$)/i); return en.length?en:vs;
    // ...o sea que en una maquina sin voces en espanol (Windows de fabrica:
    // David, Mark y Zira, las tres en-US) el pool terminaba siendo el INGLES.
    // Zira pasa el filtro "femenina", pickVoice() la elegia, y Tlamatini leia
    // castellano con boca inglesa: exactamente el acento que Angela oye.
    // Vacio es la respuesta correcta: speak() se va por Piper (es_MX-claude-
    // high, femenina) y si Piper tampoco esta, SE QUEDA CALLADA.
    return [];
  }
  // ⛔ VOZ FEMENINA SIEMPRE - UNA VOZ MASCULINA ESTA PROHIBIDA (Angela).
  // Tlamatini es mujer. Una voz de hombre NO es un sustituto aceptable en
  // NINGUN caso, en NINGUNA parte.
  //
  // Este filtro tenia un hoyo: la ultima linea era `fem=pool.slice()`, que
  // devolvia TODO el pool -- voces masculinas incluidas -- cuando ningun
  // nombre coincidia con el patron femenino. En una maquina cuyas voces en
  // espanol son todas masculinas (o cuyos nombres no reconocemos), Tlamatini
  // hablaba con voz de HOMBRE. Ahora esa rama devuelve VACIO.
  //
  // Vacio => pickVoice() regresa null => speak() se va por Piper (es_MX,
  // femenina) y si tampoco esta, SE QUEDA CALLADA. El silencio es la unica
  // alternativa aceptable: es exactamente la misma regla que aplica el agent
  // Talker (MaleVoiceForbiddenError) y la misma que aplica tts_piper.py al
  // negarse a leer espanol con una voz inglesa.
  function femaleVoices(){
    var pool=spanishPool();
    var fem=pool.filter(function(v){var n=(v.name||'');return FEMALE_RE.test(n) && !MALE_RE.test(n);});
    // Segundo intento: cualquier voz que NO sea masculina reconocida.
    if(!fem.length) fem=pool.filter(function(v){return !MALE_RE.test(v.name||'');});
    // NO hay tercer intento. Antes aqui se devolvia el pool completo.
    return fem;
  }
  var DEF={mode:'notify',voiceURI:'',volume:100,rate:1,pitch:1.05};
  function loadSettings(){ try{var s=JSON.parse(localStorage.getItem('tlm_voice_settings')||'{}');return Object.assign({},DEF,s);}catch(e){return Object.assign({},DEF);} }
  function saveSettings(s){ try{localStorage.setItem('tlm_voice_settings',JSON.stringify(s));}catch(e){} }
  var settings=loadSettings();
  function pickVoice(){
    var fem=femaleVoices(); if(!fem.length)return null;
    // La voz guardada solo vale si es en ESPANOL. Si quedo grabada una
    // inglesa (Zira) de una version anterior, se ignora: una preferencia
    // vieja no puede devolverle el acento ingles.
    if(settings.voiceURI){
      var m=fem.filter(function(v){
        return v.voiceURI===settings.voiceURI && /^es(-|_)/i.test(v.lang||'');
      });
      if(m.length)return m[0];
    }
    // Primero las mexicanas (Windows: Sabina / Dalia; Google: español),
    // luego cualquier otro espanol. NO HAY TERCER ESCALON.
    var mex=fem.filter(function(v){return /^es[-_]MX/i.test(v.lang||'');});
    if(mex.length){
      var mexPref=mex.filter(function(v){return /sabina|dalia|renata|ximena|esperanza/i.test(v.name||'');});
      return (mexPref[0]||mex[0]);
    }
    var esAny=fem.filter(function(v){return /^es(-|_)/i.test(v.lang||'');});
    if(esAny.length) return esAny[0];
    // ⛔ Antes aqui se prefería /zira|jenny|aria|samantha|hazel/ "para que una
    // maquina sin voz en espanol igual hablara". Hablaba, si — en INGLES.
    // Nada que no sea espanol sale por esta boca: null manda a Piper, y si
    // Piper no esta, al silencio.
    return null;
  }
  var _primed=false;
  function prime(){ if(_primed)return; _primed=true; try{ var u=new SpeechSynthesisUtterance(' '); u.volume=0; window.speechSynthesis.speak(u);}catch(e){} }
  var _keep=null;
  function keepAlive(on){ if(on){ if(_keep)return; _keep=setInterval(function(){ try{ if(window.speechSynthesis.speaking) window.speechSynthesis.resume(); else {clearInterval(_keep);_keep=null;} }catch(e){} },4000);} else { if(_keep){clearInterval(_keep);_keep=null;} } }
  function chunk(text){
    text=(text||'').replace(/\s+/g,' ').trim(); if(!text)return [];
    var parts=text.match(/[^.!?;:]+[.!?;:]?/g)||[text];
    var out=[],buf='';
    parts.forEach(function(p){ p=p.trim(); if(!p)return;
      if((buf+' '+p).length>170){ if(buf)out.push(buf); if(p.length>170){ for(var i=0;i<p.length;i+=170)out.push(p.slice(i,i+170)); buf=''; } else buf=p; }
      else buf=(buf?buf+' ':'')+p;
    });
    if(buf)out.push(buf); return out;
  }
  // Is ANY Spanish voice installed on this machine?
  // Angela, 2026-07-29: on a stock Windows install the only TTS voices are
  // David / Mark / Zira, all en-US. The es-MX ladder below then has nothing
  // Spanish to choose from and falls through to English — and an English
  // voice reading Spanish text is the accent she heard.
  function spanishVoiceAvailable(){
    // ⚠️ TIENE QUE PREGUNTAR LO MISMO QUE spanishPool(). Antes preguntaba
    // por CUALQUIER /^es/, incluido es-ES. En una maquina que solo tiene
    // castellano de Espana esto decia "si hay", speak() se iba por el
    // navegador, pickVoice() devolvia null (porque el pool ya no acepta
    // es-ES)... y el navegador hablaba con su voz POR DEFECTO, que es
    // inglesa. Preguntar exactamente por lo que el pool acepta cierra ese
    // hoyo: si no hay voz LATINOAMERICANA, nos vamos por Piper o al silencio.
    try{ return spanishPool().length > 0; }
    catch(e){ return false; }
  }
  var _warnedNoEs=false;
  function warnNoSpanishVoice(){
    if(_warnedNoEs)return; _warnedNoEs=true;
    try{
      window.TLM_VOICE_NO_SPANISH=true;
      console.warn('[Tlamatini] Todavía no tengo una voz en español en este equipo, '
        +'así que NO voy a hablar: leer español con una voz en inglés suena mal y '
        +'prefiero quedarme callada a hacerlo mal. Mi voz mexicana (Piper) se instala '
        +'sola, sin permisos de administrador, en '
        +'%LOCALAPPDATA%\\Tlamatini\\piper — corre el instalador de Tlamatini o el '
        +'comando:  python -c "from agent import tts_piper; tts_piper.ensure_ready()"');
      var note=document.getElementById('tlm-voice-missing-note');
      if(note)note.style.display='';
    }catch(e){}
  }

  // ---- MI PROPIA VOZ MEXICANA (Piper, del lado del servidor) ---------------
  // Windows only ships en-US voices, so when speechSynthesis has nothing in
  // Spanish the audio is synthesised by the server (agent/tts_piper.py) and
  // played back here. Everything degrades to silence, never to English.
  var _srvVoice = null;        // null = unknown, true = usable, false = absent
  var _srvQueue = [];          // pending utterances, kept in order
  var _srvAudio = null;        // the <audio> currently playing
  function _csrf(){
    try{ var m=document.cookie.match(/(?:^|; )csrftoken=([^;]+)/); return m?decodeURIComponent(m[1]):''; }
    catch(e){ return ''; }
  }
  function _srvStop(){
    _srvQueue.length=0;
    if(_srvAudio){
      try{ _srvAudio.pause(); }catch(e){}
      try{ URL.revokeObjectURL(_srvAudio.src); }catch(e){}
      _srvAudio=null;
    }
    try{ keepAlive(false); }catch(e){}
  }
  function _srvNext(){
    if(_srvAudio || !_srvQueue.length){
      if(!_srvAudio && !_srvQueue.length){ try{ keepAlive(false); }catch(e){} }
      return;
    }
    var item=_srvQueue.shift();
    fetch('/agent/tts/',{
      method:'POST',
      credentials:'same-origin',
      headers:{'Content-Type':'application/json','X-CSRFToken':_csrf()},
      body:JSON.stringify({text:item.text})
    }).then(function(r){
      // 204 = the server has no Spanish voice either. Stay quiet, stop asking.
      if(r.status===204){ _srvVoice=false; _srvStop(); warnNoSpanishVoice(); return null; }
      if(!r.ok){ _srvStop(); return null; }
      _srvVoice=true;
      return r.blob();
    }).then(function(blob){
      if(!blob){ return; }
      var a=new Audio(URL.createObjectURL(blob));
      a.volume=Math.max(0,Math.min(1,(item.volume==null?1:item.volume)));
      try{ a.playbackRate=Math.max(0.5,Math.min(2,item.rate||1)); }catch(e){}
      _srvAudio=a;
      a.onended=a.onerror=function(){
        try{ URL.revokeObjectURL(a.src); }catch(e){}
        _srvAudio=null; _srvNext();
      };
      a.play().catch(function(){ _srvAudio=null; _srvNext(); });
    }).catch(function(){ _srvStop(); });
  }
  function speakViaServer(text,opts){
    if(_srvVoice===false){ warnNoSpanishVoice(); return; }
    var s=loadSettings(); settings=s;
    if(!(opts&&opts.queue)) _srvStop();
    var pieces=chunk(text); if(!pieces.length)return;
    keepAlive(true);
    pieces.forEach(function(p){
      _srvQueue.push({text:p, volume:(s.volume||100)/100, rate:s.rate||1});
    });
    _srvNext();
  }

  // ─── ¿ESTE TEXTO YA VIENE EN CASTELLANO? ────────────────────────────────
  // Espejo en JS de tts_piper._tiene_marca_de_castellano. Exige una marca
  // POSITIVA de castellano; NO pregunta "¿parece ingles?", porque esa
  // pregunta contesta "no" ante cualquier duda y por eso dejaba pasar
  // frases cortas como "Save" o "Please wait", que salian EN INGLES.
  //
  // ⚠️ ESTAS LISTAS SON UN SUBCONJUNTO DE LAS DEL SERVIDOR, A PROPOSITO.
  // Quedarse corto es seguro: manda mas texto a Piper, que sabe traducir.
  // Pasarse es lo unico peligroso: deja salir ingles por la bocina. Por eso
  // la guarda comprueba SUBCONJUNTO y no igualdad — la lista de Python puede
  // crecer sin romper nada. Guarda: agent/test_sin_respaldo_ingles.py.
  var _PAL_ES = [
    'abrir','acaba','acabo','adios','agente','agentes','ahora','ajustes','al',
    'algo','alguien','alli','aqui','archivo','archivos','ayuda','bien',
    'bienvenida','bienvenido','borrada','borrado','borrar','buenas','buenos',
    'buscar','busqueda','cambio','cambios','cargando','carpeta','carpetas',
    'cerrar','como','con','contrasena','correcta','correcto','correo',
    'corriendo','creada','creado','cuando','de','decir','del','dias','dice',
    'dijo','disculpa','donde','el','empezar','encontrar','entre','era','eran',
    'eres','es','esa','escuchar','ese','esperando','esta','estamos','estar',
    'estas','este','esto','estoy','exitosa','exitoso','fallida','fallido',
    'favor','gracias','guardada','guardado','guardar','hablar','hace','hacer',
    'haces','hago','hecha','hecho','herramienta','herramientas','hola','la',
    'las','lista','listo','los','luego','mas','menos','mensaje','mensajes',
    'mostrar','mucho','muy','nada','nadie','no','noches','nunca','pantalla',
    'para','perdon','pero','poco','poner','por','porque','pregunta','prueba',
    'pruebas','puede','puedes','puedo','que','quiere','quieres','quiero',
    'raton','respuesta','resultado','resultados','sacar','seguir','senor',
    'senora','senorita','ser','si','siempre','sin','sobre','somos','son',
    'soy','tambien','tardes','teclado','tengo','terminada','terminado',
    'terminar','tiene','tienes','todavia','un','una','unas','unos','usuaria',
    'usuario','vamos','ventana','ventanas','voy','ya',
  ];
  var _SET_ES = (function(){ var o={}; for(var i=0;i<_PAL_ES.length;i++)o[_PAL_ES[i]]=1; return o; })();
  var _SUF_ES = ['aban', 'ando', 'aron', 'cion', 'ción', 'dad', 'endo', 'iendo', 'mente', 'sion', 'sión'];
  var _RE_ACENTO = /[áéíóúüñÁÉÍÓÚÜÑ¿¡]/;
  var _RE_LIMPIA = /^[.,;:!?()[\]"']+|[.,;:!?()[\]"']+$/g;

  function pareceCastellano(text){
    var s = String(text == null ? '' : text);
    if(!s.trim()) return true;                 // vacio: no hay nada que decir
    if(_RE_ACENTO.test(s)) return true;        // acento, enye o signo de apertura
    var ws = s.split(/\s+/);
    for(var i=0;i<ws.length;i++){
      var w = ws[i].replace(_RE_LIMPIA,'').toLowerCase();
      if(!w) continue;
      if(_SET_ES[w]) return true;              // palabra funcion o de contenido
      if(w.length > 5){                        // terminacion que solo es nuestra
        for(var j=0;j<_SUF_ES.length;j++){
          if(w.slice(-_SUF_ES[j].length) === _SUF_ES[j]) return true;
        }
      }
    }
    return false;
  }

  function speak(text,opts){
    // ⛔ AQUI SE FILTRA EL TEXTO, NO SOLO LA VOZ (Angela, 2026-08-27).
    // Antes esta funcion solo elegia QUE VOZ usaba. Eso arregla el ACENTO y
    // nada mas: si la LLM contestaba en ingles, la frase inglesa se le
    // entregaba igual a speechSynthesis con u.lang='es-MX' y se oia ingles
    // con boca mexicana. El camino del servidor (tts_piper.a_castellano) si
    // filtraba el texto y devolvia 'refused:ingles'; el del navegador no.
    // Con esto los dos caminos aplican la misma regla.
    //
    // Y NO se calla de entrada: lo que no viene en castellano se manda a
    // Piper, que PRIMERO intenta traducirlo (catalogo NEPANTLA, luego el
    // Ollama local) y solo enmudece si de veras no hubo con que. Traducir
    // antes que callar; callar antes que hablar ingles.
    if(!pareceCastellano(text)){ speakViaServer(text,opts); return; }
    // ⚠️ REFUSE RATHER THAN FAKE IT.
    // Same principle the Talker agent already applies to a male voice: if the
    // right voice is not available she does NOT substitute a wrong one. An
    // English voice pronouncing Spanish is a mispronunciation, not a fallback.
    // Order matters: a real es-* browser voice is instant, so it wins; my own
    // Piper voice is the fallback; silence is the last resort.
    if(!('speechSynthesis' in window) || !spanishVoiceAvailable()){
      speakViaServer(text,opts);
      return;
    }
    var s=loadSettings(); settings=s;
    // opts.queue = true  ->  do NOT cut off what is already being said, so that
    // consecutive messages are ALL spoken, one after another, none swallowed.
    if(!(opts&&opts.queue)){ try{window.speechSynthesis.cancel();}catch(e){} }
    var pieces=chunk(text); if(!pieces.length)return;
    var v=pickVoice();
    // ⛔ SIN VOZ ELEGIDA NO SE HABLA POR EL NAVEGADOR. Si se deja pasar con
    // `v` en null, el navegador usa su voz POR DEFECTO — que en Windows es
    // inglesa — y volvemos al acento que Angela oyo. Pasa de verdad: cuando
    // las unicas voces en castellano de la maquina son masculinas,
    // femaleVoices() queda vacio y pickVoice() devuelve null. En ese caso se
    // sintetiza con MI voz (Piper es_MX, femenina) o no se dice nada.
    if(!v){ speakViaServer(text,opts); return; }
    keepAlive(true);
    pieces.forEach(function(p,i){
      var u=new SpeechSynthesisUtterance(p);
      if(v)u.voice=v;
      u.volume=Math.max(0,Math.min(1,(s.volume||100)/100));
      u.rate=s.rate||1; u.pitch=(s.pitch==null?1.05:s.pitch); u.lang=(v&&v.lang)||'es-MX';   // Spanish edition: never fall back to English
      if(i===pieces.length-1)u.onend=function(){
        // only stand down once NOTHING else is still speaking or queued
        try{ if(!window.speechSynthesis.speaking && !window.speechSynthesis.pending) keepAlive(false); }
        catch(e){ keepAlive(false); }
      };
      try{window.speechSynthesis.speak(u);}catch(e){}
    });
  }
  // ---- STOP TALKING, RIGHT NOW -------------------------------------------
  // Kills whatever is being said AND everything still queued behind it.
  function stopSpeaking(){
    try{ window.speechSynthesis.cancel(); }catch(e){}
    try{ window.speechSynthesis.cancel(); }catch(e){}   // Chrome sometimes needs a 2nd
    try{ _srvStop(); }catch(e){}                        // ...and my own Piper audio
    try{ keepAlive(false); }catch(e){}
  }
  // Turn the voice OFF for good (persists) - or back ON.
  function setSilent(on){
    var s=loadSettings(); s.mode=on?'silent':'notify'; saveSettings(s);
    if(on)stopSpeaking();
    return s.mode;
  }
  window.TLM_VOICE={speak:speak,notify:function(){speak('Tu request está completa.');},femaleVoices:femaleVoices,pickVoice:pickVoice,loadSettings:loadSettings,saveSettings:saveSettings,prime:prime,stop:stopSpeaking,setSilent:setSilent};
  try{ if(window.speechSynthesis) window.speechSynthesis.onvoiceschanged=function(){}; }catch(e){}
  // ESC anywhere = shut up immediately.  Ctrl+Shift+M = mute for good / unmute.
  document.addEventListener('keydown',function(e){
    try{
      if(e.key==='Escape'){ stopSpeaking(); return; }
      if(e.ctrlKey&&e.shiftKey&&(e.key==='M'||e.key==='m')){
        e.preventDefault();
        var m=setSilent(loadSettings().mode!=='silent');
        var b=document.getElementById('tlm-avatar-bubble');
        if(b){ b.textContent=(m==='silent')?'Voz DESACTIVADA':'Voz ACTIVADA'; b.classList.add('tlm-show');
               clearTimeout(b._t); b._t=setTimeout(function(){b.classList.remove('tlm-show');},2600); }
      }
    }catch(err){}
  },true);
  document.addEventListener('click',prime,{once:true});
  document.addEventListener('keydown',prime,{once:true});

  ready(function(){
    var dock=document.getElementById('tlm-avatar-dock');
    var bubble=document.getElementById('tlm-avatar-bubble');
    var submit=document.getElementById('chat-message-submit');
    var input=document.getElementById('chat-message-input');
    var chatLog=document.getElementById('chat-log');
    var uname='amiga';
    try{ var el=document.getElementById('user_username'); if(el){var raw=JSON.parse(el.textContent||'""'); if(raw){uname=String(raw).charAt(0).toUpperCase()+String(raw).slice(1);}} }catch(e){}

    function pick(a){ return a[Math.floor(Math.random()*a.length)]; }
    function idlePhrase(){ return pick([
      "Aquí Tlamatini, "+uname+" - la que sabe, lista para aprender contigo.",
      uname+", estoy despierta y afilada. Ponme algo difícil.",
      "Todo funcionando, "+uname+". ¿Qué construimos hoy?",
      "Lista y escuchando, "+uname+". Dame un reto de verdad.",
      "Aquí te apoyo, "+uname+". Tú dime y me muevo.",
      "En espera, "+uname+". Hagamos algo que valga la pena recordar.",
      "Todos los circuitos en calma, "+uname+". Pregúntame lo que sea.",
      "Aquí y concentrada, "+uname+". ¿Cuál es la misión?"
    ]); }
    function busyPhrase(){ return pick([
      "Ya voy, "+uname+" - los threads girando, ya casi.",
      "Metida en el trabajo, "+uname+". Dame un segundo.",
      "Procesando esto para ti, "+uname+". Ya merito.",
      "Aguántame tantito, "+uname+" - lo estoy armando ahorita.",
      "Trabajando duro, "+uname+". Lo bueno vale la espera.",
      "Ya casi termino, "+uname+" - puliendo la última pieza.",
      "En modo total, "+uname+". No parpadees.",
      "Procesando, "+uname+" - ya casi lo tengo."
    ]); }
    // Fixed completion notice - one exact line, never randomised.
    var COMPLETE_PHRASE="Tu request está completa.";
    var CANCEL_PHRASE="Cancelaste la tarea, estoy lista para nuevas instrucciones.";
    // The FIXED messages are spoken EXACTLY AS WRITTEN - never paraphrased.
    // This only strips what must not be read aloud: markup, the username header
    // and the timestamp, and the END-RESPONSE sentinel.
    function plainText(m){
      var s=String(m==null?'':m);
      if(s.indexOf('<')>=0){
        try{
          var d=document.createElement('div'); d.innerHTML=s;
          d.querySelectorAll('script,style,button,.copy-button,.username,.message-timestamp,'
            +'.automated-message-execreport,.exec-report-table,.create-flow').forEach(function(n){try{n.remove();}catch(e){}});
          s=d.textContent||'';
        }catch(e){}
      }
      s=s.replace(/END-RESPONSE/g,'');
      s=s.replace(/^\s*Tlamatini\s*\([^)]*\)\s*/i,'');                 // "Tlamatini (2026/07/18 01:04:16.194)"
      s=s.replace(/\(\s*\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}[^)]*\)/g,' '); // any leftover timestamp
      s=s.replace(/\s+/g,' ').trim();
      return s.length>900?s.slice(0,900):s;
    }

    // Voice is ON for every fixed phrase unless the user picked "Silent".
    function voiceOn(){ try{ return loadSettings().mode!=='silent'; }catch(e){ return true; } }

    // Every PRE-ESTABLISHED phrase goes through here: it always shows the balloon
    // and always SPEAKS it aloud - the only exception is Silent mode.
    // `key` + `gapMs` stop the same state from repeating itself back-to-back
    // (e.g. our own "on it" and the server's "being processed" placeholder).
    var _said={};
    function announce(key,text,gapMs){
      if(!text)return false;
      var now=Date.now();
      if(key){ if(now-(_said[key]||0)<(gapMs==null?8000:gapMs))return false; _said[key]=now; }
      showBubble(text);
      if(!voiceOn())return true;
      // QUEUE it: a second message must never cut the first one short.
      prime(); speak(text,{queue:true});
      return true;
    }

    // What KIND of message is this? Every non-'answer' kind is a fixed/system
    // message that Tlamatini must speak with her own matching phrase.
    function classify(txt){
      var t=(txt||'').trim(); if(!t)return 'skip';
      var tl=t.toLowerCase();
      try{ if(window.isSelfHealingStatusMessage&&window.isSelfHealingStatusMessage(t))return 'retry'; }catch(e){}
      try{ if(window.isSessionRestoredInfoMessage&&window.isSessionRestoredInfoMessage(t))return 'restored'; }catch(e){}
      // FIRST-PERSON wording (2026-07-29) plus the older third-person forms.
      // She now says "Hola, soy Tlamatini, estoy lista para platicar contigo";
      // matching only the old 'tlamatini está lista' would leave her avatar
      // stuck on the wrong expression. Keep BOTH — a stale phrasing costs
      // nothing, a missed one shows the wrong mood.
      if(tl.indexOf('your agent is ready')>=0||tl.indexOf('you can now start chatting')>=0
         ||tl.indexOf('estoy lista para platicar')>=0||tl.indexOf('soy tlamatini')>=0
         ||tl.indexOf('tlamatini está lista')>=0||tl.indexOf('puedes platicar con ella')>=0)return 'ready';
      if(tl.indexOf('you cancelled')>=0||tl.indexOf('you canceled')>=0
         ||tl.indexOf('cancelaste')>=0||tl.indexOf('canceló la generación')>=0)return 'cancel';
      if(tl.indexOf('execution interrupted')>=0||tl.indexOf('ejecución interrumpida')>=0)return 'interrupted';
      // 'reformula lo que me pediste' = el rechazo de forma-de-prompt en
      // español (rag/interface.py). Se usa la frase LARGA a propósito: un
      // 'reformula' pelón también pegaría con el rechazo de path relativo
      // ("Reformula tu prompt, por favor"), que NO es el mismo caso.
      if(tl.indexOf('pregunta reformulada')>=0||tl.indexOf('please rephrase')>=0
         ||tl.indexOf('reformula lo que me pediste')>=0)return 'rephrase';
      if((tl.indexOf('not ready')>=0&&tl.indexOf('agent')>=0)
         ||tl.indexOf('todavía no estoy lista')>=0||tl.indexOf('no puedo procesar tus requests')>=0
         ||tl.indexOf('todavía no está lista')>=0||tl.indexOf('no puede procesar tus requests')>=0)return 'notready';
      try{ if(window.isBusyMessageRequest&&window.isBusyMessageRequest(t))return 'busy'; }catch(e){}
      try{ if(window.isBusyMessageContext&&window.isBusyMessageContext(t))return 'busy'; }catch(e){}
      if(tl.indexOf('your request is being processed')>=0||tl.indexOf('being processed by tlamatini')>=0
         ||tl.indexOf('please wait a moment')>=0||tl.indexOf('loading the context')>=0
         ||tl.indexOf('estoy procesando tu request')>=0||tl.indexOf('me estoy cargando')>=0
         ||tl.indexOf('espérame tantito')>=0||tl.indexOf('esperame tantito')>=0
         ||tl.indexOf('está procesando tu request')>=0||tl.indexOf('cargando el context')>=0
         ||tl.indexOf('espera un momento')>=0||tl.indexOf('se está cargando')>=0)return 'busy';
      if(/^(please wait|loading|thinking|working on it|one moment|processing|espera|cargando|pensando|procesando|un momento)/i.test(t))return 'busy';
      if(tl.indexOf('out of the root directory')>=0||tl.indexOf('outside the application root')>=0
         ||tl.indexOf('fuera del root directory')>=0||tl.indexOf('fuera del root path')>=0
         ||tl.indexOf('no es una carpeta')>=0
         ||(tl.indexOf('no existe')>=0&&(tl.indexOf('directorio')>=0||tl.indexOf('carpeta')>=0))
         ||tl.indexOf('not a valid directory')>=0||(tl.indexOf('directory')>=0&&tl.indexOf('does not exist')>=0))return 'error';
      return 'answer';
    }

    function isWorking(){
      try{
        if(input&&input.disabled)return true;
        if(submit){var t=(submit.textContent||'').trim().toLowerCase(); if(t.indexOf('cancel')>=0||t.indexOf('stop')>=0)return true;}
        if(window.inLongOperation===true)return true;
      }catch(e){}
      return false;
    }
    function isCancelButton(){ try{ var t=(submit&&submit.textContent||'').trim().toLowerCase(); return t.indexOf('cancel')>=0||t.indexOf('stop')>=0; }catch(e){return false;} }
    function showBubble(t){ if(!bubble)return; bubble.textContent=t;
      try{ if(dock){ var r=dock.getBoundingClientRect(); bubble.style.position='fixed'; bubble.style.left='auto'; bubble.style.top='auto';
        bubble.style.right=Math.max(8,(window.innerWidth-r.right))+'px'; bubble.style.bottom=(window.innerHeight-r.top+10)+'px'; } }catch(e){}
      bubble.classList.add('tlm-show'); clearTimeout(bubble._t); bubble._t=setTimeout(function(){bubble.classList.remove('tlm-show');},4600); }

    // ---- run lifecycle: pending -> saw-work -> completed / cancelled ----
    var _pending=false, _seenWork=false, _spoken=false;
    function markSend(){
      _pending=true; _seenWork=false; _spoken=false;
      _said={};        // new run -> every fixed message may be announced again
      // NOTE: nothing is invented here. The server's own fixed message
      // ("Your request is being processed by Tlamatini. Please wait a moment.")
      // arrives a moment later and is spoken VERBATIM by onTlamatiniMessage.
    }
    function lastBotAnswer(){ try{ var arr=chatLog?chatLog.querySelectorAll('.bot-message'):[]; return arr.length?arr[arr.length-1]:null; }catch(e){return null;} }
    function extractAnswer(node){
      try{
        var body=node.querySelector('.automated-message-body')||node.querySelector('.automated-message');
        if(!body)return '';
        var clone=body.cloneNode(true);
        clone.querySelectorAll('.automated-message-execreport,.exec-report-table,.exec-denied-banner,button,.create-flow,.username,.message-timestamp,.copy-button').forEach(function(n){try{n.remove();}catch(e){}});
        return (clone.textContent||'').replace(/END-RESPONSE/g,'').trim();
      }catch(e){return '';}
    }
    // A "status" message is anything that is NOT the real final answer.
    function isStatusMsg(txt){ var k=classify(txt); return k!=='answer'; }

    function doComplete(){
      if(_spoken)return; _spoken=true; _pending=false;
      var s=loadSettings();
      showBubble(COMPLETE_PHRASE);              // balloon always
      if(s.mode==='silent')return;              // Silent: the ONLY mute case
      setTimeout(function(){
        var text=COMPLETE_PHRASE;               // exact fixed line
        if(s.mode==='speak'){
          var last=lastBotAnswer(); var a=last?extractAnswer(last):'';
          if(a && !isStatusMsg(a)) text=a;      // read the ANSWER itself, verbatim
        }
        prime(); speak(text);
      }, 220);
    }
    function doCancelSpeak(){
      _pending=false; _spoken=true;
      try{window.speechSynthesis.cancel();}catch(e){}
      _said['cancel']=0;                        // a cancel always gets announced
      announce('cancel',CANCEL_PHRASE,0);
    }

    if(submit)submit.addEventListener('click',function(){ if(isCancelButton()){ doCancelSpeak(); } else { markSend(); } });
    if(input)input.addEventListener('keydown',function(e){ if(e.key==='Enter'&&!e.shiftKey && !isCancelButton()){ markSend(); } });
    var _cf=document.getElementById('chat-form'); if(_cf)_cf.addEventListener('submit',function(){ if(!isCancelButton()){ markSend(); } });

    // (completion is handled below by hooking the app's own appendChatMessage)

    if(dock){
      var faceOuter=document.getElementById('tlm-face-outer');
      var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var IMGS={ eo_mc:document.getElementById('tlm-s-eo-mc'), ec_mc:document.getElementById('tlm-s-ec-mc'),
                 eo_mo:document.getElementById('tlm-s-eo-mo'), ec_mo:document.getElementById('tlm-s-ec-mo') };
      var stt={eyesOpen:true, mouthOpen:false};
      function render(){
        var key=(stt.eyesOpen?'eo':'ec')+'_'+(stt.mouthOpen?'mo':'mc');
        for(var k in IMGS){ if(IMGS[k]) IMGS[k].classList.toggle('tlm-on', k===key); }
      }
      render();
      function layoutFace(){
        if(!faceOuter)return;
        var pad=5, pw=dock.clientWidth-2*pad, ph=dock.clientHeight-2*pad;
        if(pw<=0||ph<=0)return;
        var ar=1, iw,ih;
        if(pw/ph>ar){ih=ph;iw=ph*ar;}else{iw=pw;ih=pw/ar;}
        faceOuter.style.left=(pad+(pw-iw)/2)+'px';faceOuter.style.top=(pad+(ph-ih)/2)+'px';
        faceOuter.style.width=iw+'px';faceOuter.style.height=ih+'px';
      }
      layoutFace();
      if(window.ResizeObserver){try{new ResizeObserver(layoutFace).observe(dock);}catch(e){}}
      window.addEventListener('resize',layoutFace);
      function blink(done){ stt.eyesOpen=false; render(); setTimeout(function(){ stt.eyesOpen=true; render(); if(done)done(); }, 190); }
      function scheduleBlink(){
        if(reduce)return;
        setTimeout(function(){
          if(document.hidden){scheduleBlink();return;}
          blink(function(){ if(Math.random()<0.12){ setTimeout(function(){blink(scheduleBlink);},170); } else scheduleBlink(); });
        },2800+Math.random()*3800);
      }
      scheduleBlink();
      setInterval(function(){
        var sp=false; try{ sp=window.speechSynthesis&&window.speechSynthesis.speaking; }catch(e){}
        if(sp){ stt.mouthOpen=!stt.mouthOpen; render(); }
        else if(stt.mouthOpen){ stt.mouthOpen=false; render(); }
      }, 150);
      // CLICK HER WHILE SHE IS TALKING = STOP IMMEDIATELY (never talk more).
      // Click when she is quiet = she greets you. DOUBLE-CLICK = mute for good.
      function onClick(){
        prime();
        var busy=false;
        try{ busy=window.speechSynthesis.speaking||window.speechSynthesis.pending; }catch(e){}
        if(busy){ stopSpeaking(); showBubble('Voz detenida.'); return; }
        announce(null,(isWorking()?busyPhrase():idlePhrase()),0);
      }
      dock.addEventListener('click',onClick);
      dock.addEventListener('dblclick',function(e){
        e.preventDefault();
        var m=setSilent(loadSettings().mode!=='silent');
        stopSpeaking();
        showBubble(m==='silent'?'Voz DESACTIVADA (doble clic otra vez para ACTIVARLA)':'Voz ACTIVADA');
      });
      dock.addEventListener('keydown',function(e){ if(e.key==='Enter'||e.key===' '){e.preventDefault();onClick();} });
      dock.title='Clic = deja de hablar / saluda  ·  Doble clic = silenciar  ·  Esc = detener  ·  Ctrl+Shift+M = silenciar';
    }

    // ---- completion: hook the app's OWN renderer (bulletproof, content-based).
    // appendChatMessage(username, message, ...) runs for EVERY message. A Tlamatini
    // message that is NOT a busy / loading / self-healing / status line IS the real
    // final answer (the app's own catch-all `else` branch that re-enables controls).
    // Speak ONLY then - never on the "Please wait a moment" placeholder or a status frame.
    // EVERY Tlamatini message is spoken: a real answer -> the completion phrase
    // (plus the answer itself in "speak" mode); any FIXED/system message -> its own
    // matching pre-established phrase. Silent mode is the only thing that mutes her.
    // Swallow only the burst of OLD messages replayed at page load; after this
    // the avatar speaks everything Tlamatini says.
    var _armed=false; setTimeout(function(){ _armed=true; },1500);

    function onTlamatiniMessage(message){
      if(!_armed)return;                       // history replay, not live speech
      var text=plainText(message);
      if(!text)return;
      var kind=classify(message);
      // The REAL answer to a request WE sent: "speak" mode reads it aloud,
      // "notify" mode says the fixed completion line instead.
      if(kind==='answer'&&_pending&&!_spoken){ doComplete(); return; }
      // EVERYTHING ELSE Tlamatini says - every fixed/system message, and any
      // message arriving with no request pending - is spoken WORD FOR WORD.
      if(kind==='cancel'||kind==='interrupted'||kind==='rephrase'||kind==='error'){
        _pending=false; _spoken=true;          // the run is over
      }
      // dedupe on the TEXT itself, so two DIFFERENT messages BOTH get spoken
      announce('t:'+text.slice(0,80),text,2500);
    }
    var _hooked=false;
    try{
      if(typeof window.appendChatMessage==='function'){
        var _origAppend=window.appendChatMessage;
        window.appendChatMessage=function(username,message){
          var r=_origAppend.apply(this,arguments);
          try{ if(username==='Tlamatini'){ var msg=message; setTimeout(function(){ onTlamatiniMessage(msg); },120); } }catch(e){}
          return r;
        };
        _hooked=true;
      }
    }catch(e){}
    // fallback DOM observer (only if the renderer could not be hooked)
    if(!_hooked && chatLog && ('MutationObserver' in window)){
      try{chatLog.querySelectorAll('.bot-message').forEach(function(b){b.setAttribute('data-tlm-spoken','1');});}catch(e){}
      var _deb=null;
      var obs=new MutationObserver(function(muts){
        if(!_pending||_spoken)return;
        var target=null;
        muts.forEach(function(mu){ Array.prototype.forEach.call(mu.addedNodes||[],function(n){
          if(n.nodeType!==1)return;
          var bm=(n.classList&&n.classList.contains('bot-message'))?n:(n.querySelector?n.querySelector('.bot-message'):null);
          if(bm&&!bm.getAttribute('data-tlm-spoken')) target=bm;
        }); });
        if(!target)return;
        clearTimeout(_deb);
        _deb=setTimeout(function(){
          if(_spoken||!_pending)return;
          var ans=extractAnswer(target); if(!ans||isStatusMsg(ans))return;
          target.setAttribute('data-tlm-spoken','1'); doComplete();
        },350);
      });
      try{obs.observe(chatLog,{childList:true,subtree:true});}catch(e){}
    }

    var overlay=document.getElementById('tlm-voice-overlay');
    function fillVoices(){
      var sel=document.getElementById('tlm-voice-select'); if(!sel)return;
      var fem=femaleVoices(); sel.innerHTML='';
      fem.forEach(function(v){var o=document.createElement('option');o.value=v.voiceURI;o.textContent=v.name+' ('+v.lang+')';sel.appendChild(o);});
      var s=loadSettings(); if(s.voiceURI)sel.value=s.voiceURI; else { var pv=pickVoice(); if(pv)sel.value=pv.voiceURI; }
    }
    function syncDialog(){
      var s=loadSettings();
      var vol=document.getElementById('tlm-voice-volume'),rate=document.getElementById('tlm-voice-rate'),pitch=document.getElementById('tlm-voice-pitch');
      if(vol){vol.value=s.volume;document.getElementById('tlm-voice-vol-val').textContent=s.volume+'%';}
      if(rate){rate.value=s.rate;document.getElementById('tlm-voice-rate-val').textContent=(s.rate).toFixed(2)+'x';}
      if(pitch){pitch.value=s.pitch;document.getElementById('tlm-voice-pitch-val').textContent=(s.pitch).toFixed(2);}
      var r=document.querySelector('input[name="tlm-voice-mode"][value="'+s.mode+'"]'); if(r)r.checked=true;
      fillVoices();
    }
    function readDialog(){
      var s=loadSettings();
      var vol=document.getElementById('tlm-voice-volume'),rate=document.getElementById('tlm-voice-rate'),pitch=document.getElementById('tlm-voice-pitch'),sel=document.getElementById('tlm-voice-select');
      if(vol)s.volume=parseInt(vol.value,10);
      if(rate)s.rate=parseFloat(rate.value);
      if(pitch)s.pitch=parseFloat(pitch.value);
      if(sel&&sel.value)s.voiceURI=sel.value;
      var r=document.querySelector('input[name="tlm-voice-mode"]:checked'); if(r)s.mode=r.value;
      return s;
    }
    window.OpenVoiceDialog=function(ev){ if(ev&&ev.preventDefault)ev.preventDefault(); prime(); if(!overlay)return; syncDialog(); overlay.style.display='flex'; };
    function closeDialog(){ if(overlay)overlay.style.display='none'; }
    if(overlay){
      var x=document.getElementById('tlm-voice-close'); if(x)x.addEventListener('click',closeDialog);
      /* sin cierre por click afuera: se cierra con la X */
      var save=document.getElementById('tlm-voice-save'); if(save)save.addEventListener('click',function(){ saveSettings(readDialog()); closeDialog(); });
      var test=document.getElementById('tlm-voice-test'); if(test)test.addEventListener('click',function(){ saveSettings(readDialog()); prime(); speak("¡Hola "+uname+"! Esta es mi voz."); });
      ['tlm-voice-volume','tlm-voice-rate','tlm-voice-pitch'].forEach(function(id){
        var elx=document.getElementById(id); if(!elx)return;
        elx.addEventListener('input',function(){
          if(id==='tlm-voice-volume')document.getElementById('tlm-voice-vol-val').textContent=elx.value+'%';
          if(id==='tlm-voice-rate')document.getElementById('tlm-voice-rate-val').textContent=parseFloat(elx.value).toFixed(2)+'x';
          if(id==='tlm-voice-pitch')document.getElementById('tlm-voice-pitch-val').textContent=parseFloat(elx.value).toFixed(2);
        });
      });
    }
  });
})();
