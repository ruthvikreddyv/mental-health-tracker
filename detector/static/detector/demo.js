/* Mental Health Detector: browser demo plus Supabase Auth / Django API-backed private accounts. */
(() => {
  'use strict';
  const KEY='mindful_space_private_demo_v2';
  const THEME='mindful_space_theme';
  const blank=()=>({journals:[],checkins:[]});
  const $=id=>document.getElementById(id);
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const isoDate=d=>new Date(d||Date.now());
  const prettyDate=d=>isoDate(d).toLocaleDateString(undefined,{day:'numeric',month:'short',year:'numeric'});
  const shortDate=d=>isoDate(d).toLocaleDateString(undefined,{day:'numeric',month:'short'});
  const setText=(id,value)=>{const el=$(id);if(el)el.textContent=String(value)};
  let local=blank(), state=blank(), cloud=null, user=null, cloudReady=false, mood=null, authMode='login', busy=false;
  try{const saved=JSON.parse(localStorage.getItem(KEY)||'null');if(saved&&Array.isArray(saved.journals)&&Array.isArray(saved.checkins))local=saved;}catch(_){local=blank()}
  state=local;
  try{document.documentElement.dataset.theme=localStorage.getItem(THEME)==='dark'?'dark':'light'}catch(_){}
  const toast=(msg)=>{const el=$('app-toast');el.textContent=String(msg);el.classList.remove('hidden');clearTimeout(toast.timer);toast.timer=setTimeout(()=>el.classList.add('hidden'),4200)};
  const saveLocal=()=>{try{localStorage.setItem(KEY,JSON.stringify(local));return true}catch(_){toast('Browser storage is unavailable. Your changes may not persist.');return false}};
  const authenticated=()=>!!user;
  const toEntry=x=>({...x,at:x.at||x.created_at});
  const normalize=x=>({journals:(x.journals||[]).map(toEntry).sort((a,b)=>isoDate(b.at)-isoDate(a.at)),checkins:(x.checkins||[]).map(toEntry).sort((a,b)=>isoDate(b.at)-isoDate(a.at))});
  const getToken=async()=>{if(!cloud)throw Error('Accounts are not connected.');const {data,error}=await cloud.auth.getSession();if(error||!data.session)throw Error('Sign in to continue.');return data.session.access_token};
  const api=async(path,method='GET',value=null)=>{
    const token=await getToken();const headers={'Authorization':'Bearer '+token};if(value!==null)headers['Content-Type']='application/json';
    const response=await fetch('/api/'+path,{method,headers,body:value===null?null:JSON.stringify(value),cache:'no-store'});
    let data;try{data=await response.json()}catch(_){throw Error('The server returned an invalid response.')}
    if(!response.ok)throw Error(data.error||'Cloud operation failed.');return data;
  };
  const loadRemote=async()=>{if(!authenticated())return;try{
      const [j,c]=await Promise.all([api('journals/'),api('checkins/')]);
      state=normalize({journals:j.items,checkins:c.items});render();
    }catch(e){toast(e.message);}
  };
  const setMode=()=>{
    const account=authenticated(), ready=cloudReady;
    $('data-mode-label').textContent=account?'Encrypted connection · Cloud account':ready?'Browser-only demo · Sign in to sync':'Browser-only demo · Cloud not connected';
    document.querySelector('.data-status').classList.toggle('cloud',account);
    $('cloud-auth-open').classList.toggle('hidden',!ready||account);
    $('cloud-signout').classList.toggle('hidden',!account);
    $('privacy-status-title').textContent=account?'Private cloud account.':'Private browser demo.';
    $('privacy-status-copy').textContent=account?'Your account-specific entries are stored in Supabase and access-controlled using row-level security. Do not enter information you would not want stored online.':'This demo saves reflections in this browser’s local storage. They are not encrypted or uploaded to our server. Do not use on shared devices.';
    $('mode-footer').textContent=account?'Protected cloud account':'Private browser demo';
    $('settings-storage-note').textContent=account?'Account entries are stored in Supabase with per-user access rules. Export or delete your stored entries at any time. Demo entries are not uploaded automatically.':'Browser demo entries remain in local storage, unencrypted. Create a cloud account when storage becomes available.';
    $('import-cloud-row').classList.toggle('hidden',!account);
  };
  const setAuthMode=mode=>{
    authMode=mode;setText('auth-heading',mode==='signup'?'Create your space':'Welcome back');
    setText('auth-description',mode==='signup'?'A private space you can return to anytime.':'Sign in to access your saved reflections and check-ins.');
    $('auth-login-tab').classList.toggle('tab-selected',mode==='login');$('auth-signup-tab').classList.toggle('tab-selected',mode==='signup');
    $('auth-login-tab').setAttribute('aria-selected',String(mode==='login'));
    $('auth-signup-tab').setAttribute('aria-selected',String(mode==='signup'));
    $('auth-password').autocomplete=mode==='signup'?'new-password':'current-password';
    setText('auth-submit',mode==='signup'?'Create account →':'Sign in securely →');$('auth-error').classList.add('hidden');
  };
  const modal=show=>{ $('auth-modal').classList.toggle('hidden',!show); if(show){setAuthMode('login');$('auth-email').focus()}else if(!$('cloud-auth-open').classList.contains('hidden')) $('cloud-auth-open').focus(); };
  $('cloud-auth-open').addEventListener('click',()=>{if(cloudReady)modal(true);else toast('Account connection is not configured yet. You can explore the demo.')});
  $('auth-close').addEventListener('click',()=>modal(false));
  $('auth-modal').addEventListener('click',e=>{if(e.target===$('auth-modal'))modal(false)});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('auth-modal').classList.contains('hidden'))modal(false)});
  $('auth-login-tab').addEventListener('click',()=>setAuthMode('login'));
  $('auth-signup-tab').addEventListener('click',()=>setAuthMode('signup'));
  $('auth-form').addEventListener('submit',async e=>{
    e.preventDefault();if(busy||!cloud)return;
    const email=$('auth-email').value.trim(),password=$('auth-password').value;
    if(password.length<8){$('auth-error').textContent='Use a password of at least 8 characters.';$('auth-error').classList.remove('hidden');return}
    busy=true;$('auth-submit').disabled=true;
    try{
      const {data,error}=authMode==='signup'?await cloud.auth.signUp({email,password}):await cloud.auth.signInWithPassword({email,password});
      if(error)throw error;
      if(authMode==='signup'&&!data.session){toast('Check your email to verify your new account before signing in.');modal(false);}
      else{user=data.user;state=blank();modal(false);setMode();await loadRemote();toast('Your private account is ready.');}
    }catch(err){$('auth-error').textContent=err.message||'Unable to sign in';$('auth-error').classList.remove('hidden')}
    finally{busy=false;$('auth-submit').disabled=false}
  });
  $('cloud-signout').addEventListener('click',async()=>{
    if(cloud){await cloud.auth.signOut();}user=null;state=local;setMode();render();toast('Signed out. Demo mode is available.');
  });
  $('theme-toggle').addEventListener('click',()=>{
    const next=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=next;
    try{localStorage.setItem(THEME,next)}catch(_){}
    $('theme-toggle').textContent=next==='dark'?'☼':'☾';$('theme-toggle').setAttribute('aria-label',next==='dark'?'Switch to light mode':'Switch to dark mode');
  });
  $('theme-toggle').textContent=document.documentElement.dataset.theme==='dark'?'☼':'☾';$('theme-toggle').setAttribute('aria-label',document.documentElement.dataset.theme==='dark'?'Switch to light mode':'Switch to dark mode');
  const titles={overview:['Your day, at your pace.','A little space to notice how you’re doing.'],journal:['A page for your thoughts.','Take a moment to put things into words.'],checkin:['A gentle check-in.','No judgment. Just a moment of reflection.'],insights:['The story of your days.','Notice the little steps you’ve taken.'],support:['You deserve support.','Whatever today holds, you don’t have to face it alone.'],settings:['Your space, your choices.','Decide what you want to keep or remove.']};
  function go(view){if(!titles[view])return;
    document.querySelectorAll('[data-view]').forEach(btn=>{btn.classList.toggle('side-active',btn.dataset.view===view);btn.setAttribute('aria-current',btn.dataset.view===view?'page':'false')});
    document.querySelectorAll('.demo-view').forEach(el=>el.classList.add('hidden'));
    $(view+'-view').classList.remove('hidden');setText('view-heading',titles[view][0]);setText('view-subtitle',titles[view][1]);render();window.scrollTo({top:0,behavior:'smooth'});
  }
  document.querySelectorAll('[data-view]').forEach(btn=>btn.addEventListener('click',()=>go(btn.dataset.view)));
  document.querySelectorAll('[data-go]').forEach(btn=>btn.addEventListener('click',()=>go(btn.dataset.go)));
  setText('today-chip',new Date().toLocaleDateString(undefined,{weekday:'short',month:'short',day:'numeric'}));
  document.querySelectorAll('[data-mood]').forEach(btn=>btn.addEventListener('click',()=>{
    const val=Number(btn.dataset.mood);mood=mood===val?null:val;
    document.querySelectorAll('[data-mood]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.mood)===mood)));
  }));

  const feelings={1:'It’s okay to have a hard day.',2:'Be gentle with yourself today.',3:'Somewhere in between is perfectly okay.',4:'Hold on to what feels good.',5:'There’s room to enjoy this feeling.'};
  document.querySelectorAll('[data-mood]').forEach(btn=>btn.addEventListener('click',()=>{
    setText('mood-feedback',mood?`${feelings[mood]} We’ll attach this to your next saved journal entry.`:'Choose a mood to attach it to your next saved entry.');
  }));
  document.querySelectorAll('[data-prompt]').forEach(button=>button.addEventListener('click',()=>{
    const input=button.closest('#journal-view')?$('journal-text'):$('overview-text');
    const prompt=button.dataset.prompt||'';
    input.value=input.value.trim()?input.value.trim()+'\n\n'+prompt:prompt;
    input.focus();input.setSelectionRange(input.value.length,input.value.length);
    if(input===$('journal-text'))setText('journal-count',`${input.value.length} / 3000 characters`);
  }));
  for(const [id,saveId] of [['journal-text','journal-save'],['overview-text','quick-save']]){
    $(id).addEventListener('keydown',e=>{
      if((e.metaKey||e.ctrlKey)&&e.key==='Enter'){e.preventDefault();$(saveId).click()}
    });
  }
  // A short, opt-in breathing exercise with a visible stop action. No health claims.
  let breathTimer=null, inhale=true;
  const breathe=()=>{
    const orb=$('breath-orb');
    orb.classList.toggle('is-inhaling',inhale);
    setText('breath-message',inhale?'Breathe in, softly, for four seconds.':'Breathe out, slowly, for six seconds.');
    const duration=inhale?4000:6000;inhale=!inhale;
    breathTimer=setTimeout(breathe,duration);
  };
  const stopBreathe=()=>{
    clearTimeout(breathTimer);breathTimer=null;inhale=true;
    $('breath-orb').classList.remove('is-inhaling');
    $('breath-start').setAttribute('aria-pressed','false');
    $('breath-start').textContent='Start breathing ↗';
    setText('breath-message','Try a gentle guided breathing pause. Stop whenever you like.');
  };
  $('breath-start').addEventListener('click',()=>{
    if(breathTimer){stopBreathe();return}
    $('breath-start').setAttribute('aria-pressed','true');$('breath-start').textContent='Stop breathing';
    breathe();
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&breathTimer)stopBreathe()});
  const questions=JSON.parse($('demo-question-data').textContent);
  const survey=$('survey-questions'),labels=['Not at all','Several days','More than half the days','Nearly every day'];
  questions.forEach((question,i)=>{
    const fieldset=document.createElement('fieldset');fieldset.className='question';
    const legend=document.createElement('legend');legend.textContent=`${String(i+1).padStart(2,'0')}  ${question}`;fieldset.append(legend);
    const options=document.createElement('div');options.className='radio-list';const wrapper=document.createElement('div');
    labels.forEach((name,j)=>{
      const box=document.createElement('div'),radio=document.createElement('input'),label=document.createElement('label');
      radio.type='radio';radio.name='q'+i;radio.id=`q${i}-${j}`;radio.value=String(j);radio.required=true;
      label.htmlFor=radio.id;label.textContent=name;box.append(radio,label);wrapper.append(box);
    });options.append(wrapper);fieldset.append(options);survey.append(fieldset);
  });
  function updateProgress(){const answered=questions.filter((_,i)=>!!document.querySelector(`input[name="q${i}"]:checked`)).length;setText('survey-progress-label',`${answered} of ${questions.length} answered`);$('survey-progress').style.width=`${answered/questions.length*100}%`}
  $('checkin-form').addEventListener('change',updateProgress);
  // One question at a time is gentler than a long, scroll-heavy questionnaire.
  let questionIndex=0;
  const questionCards=Array.from(survey.querySelectorAll('.question'));
  survey.dataset.enhancedSurvey='true';
  function showQuestion(index){
    questionIndex=Math.max(0,Math.min(questions.length-1,index));
    questionCards.forEach((card,i)=>{
      card.classList.add('is-stepped');
      card.classList.toggle('is-current',i===questionIndex);
      card.setAttribute('aria-hidden',String(i!==questionIndex));
      card.querySelectorAll('input').forEach(input=>{input.disabled=i!==questionIndex});
    });
    $('question-back').classList.toggle('hidden',questionIndex===0);
    $('question-next').classList.toggle('hidden',questionIndex===questions.length-1);
    $('question-submit').classList.toggle('hidden',questionIndex!==questions.length-1);
    setText('question-helper',`Question ${questionIndex+1} of ${questions.length}`);
  }
  // Disabled questions still retain their selected radio values in the DOM. The form
  // is submitted programmatically using selected values rather than FormData.
  $('question-next').addEventListener('click',()=>{
    if(!document.querySelector(`input[name="q${questionIndex}"]:checked`)){
      toast('Choose the answer that feels closest before continuing.');return;
    }
    showQuestion(questionIndex+1);
    $('checkin-view').scrollIntoView({behavior:'smooth',block:'start'});
  });
  $('question-back').addEventListener('click',()=>showQuestion(questionIndex-1));
  showQuestion(0);

  async function addJournal(input,moodValue){
    const text=String(input||'').trim();if(!text){toast('Write a few words before saving.');return false}
    if(text.length>3000){toast('Please keep entries under 3,000 characters.');return false}
    if(busy)return false;busy=true;
    try{if(authenticated()){await api('journals/','POST',{text,mood:moodValue});await loadRemote()}
      else{const entry={id:crypto.randomUUID?crypto.randomUUID():String(Date.now()),text,mood:moodValue,at:new Date().toISOString()};local.journals.unshift(entry);if(!saveLocal()){local.journals.shift();return false}state=local;render()}
      toast('Reflection saved.');return true;
    }catch(e){toast(e.message);return false}finally{busy=false}
  }
  $('quick-save').addEventListener('click',async()=>{if(await addJournal($('overview-text').value,mood)){$('overview-text').value='';}});
  $('journal-save').addEventListener('click',async()=>{if(await addJournal($('journal-text').value,mood)){$('journal-text').value='';updateCount();go('journal')}});
  const updateCount=()=>setText('journal-count',`${$('journal-text').value.length} / 3000 characters`);
  $('journal-text').addEventListener('input',updateCount);
  $('checkin-form').addEventListener('submit',async e=>{
    e.preventDefault();if(busy)return;
    const answers=questions.map((_,i)=>{const found=document.querySelector(`input[name="q${i}"]:checked`);return found?Number(found.value):NaN});
    if(answers.some(v=>!Number.isInteger(v)||v<0||v>3)){toast('Please answer all ten questions.');return}
    const total=answers.reduce((a,b)=>a+b,0);busy=true;
    try{if(authenticated()){await api('checkins/','POST',{answers});await loadRemote()}
      else{const entry={id:crypto.randomUUID?crypto.randomUUID():String(Date.now()),answers,total,at:new Date().toISOString()};local.checkins.unshift(entry);if(!saveLocal()){local.checkins.shift();return}state=local;render()}
      $('checkin-form').reset();updateProgress();showQuestion(0);
      const risk=answers[9]>0?'<div class="notice urgent"><strong>Your safety matters.</strong> You mentioned thoughts of harm. If you feel at risk of acting on those thoughts, contact emergency services or go to the nearest emergency department and ask someone you trust to stay with you.</div>':'<div class="notice">If your feelings interfere with daily life, consider talking to a qualified mental-health professional or trusted person.</div>';
      const result=$('survey-result');result.classList.remove('hidden');result.innerHTML=`<span class="eyebrow">CHECK-IN COMPLETE</span><div class="score-circle">${total}<small>/30</small></div><h2>You made space for yourself.</h2><p>These are your answers added together—not a diagnosis, clinical scale or measure of your worth.</p>${risk}<button class="btn btn-light" id="result-close" type="button">Back to my overview →</button>`;
      $('result-close').addEventListener('click',()=>{result.classList.add('hidden');go('overview')});result.scrollIntoView({behavior:'smooth',block:'center'});toast('Check-in saved.');
    }catch(err){toast(err.message)}finally{busy=false}
  });
  const entryMarkup=x=>`<article class="entry"><div class="entry-meta"><span>${escape(prettyDate(x.at))}${x.mood?` · Mood ${escape(x.mood)}/5`:''}</span></div><p>${escape(x.text).replace(/\n/g,'<br>')}</p><button type="button" class="delete-link" data-delete="${escape(x.id)}">Delete entry</button></article>`;
  function chart(id,items,max,kind){const holder=$(id);holder.replaceChildren();if(!items.length){holder.innerHTML='<div class="empty"><p>Your activity will appear here as you add entries.</p></div>';return}
    [...items].slice(0,10).reverse().forEach(item=>{const col=document.createElement('div');col.className='activity-column';const bar=document.createElement('div');bar.className='activity-bar';const value=kind==='checkins'?item.total:1;bar.style.height=`${Math.max(6,Math.min(100,value/max*100))}%`;bar.title=kind==='checkins'?`Check-in total ${value} of 30`:'Journal entry';const label=document.createElement('span');label.textContent=shortDate(item.at);col.append(bar,label);holder.append(col)})
  }
  function render(){const entries=normalize(state).journals,checkins=normalize(state).checkins;
    setText('total-journals',entries.length);setText('total-checkins',checkins.length);setText('last-checkin',checkins.length?checkins[0].total:'—');
    setText('insight-journals',entries.length);setText('insight-checkins',checkins.length);setText('insight-latest',entries.length?shortDate(entries[0].at):'—');
    $('recent-reflections').innerHTML=entries.length?entries.slice(0,2).map(entryMarkup).join(''):'<div class="empty"><p>Your first reflection will appear here.</p></div>';
    const query=$('journal-search').value.trim().toLowerCase(),sorted=[...entries].filter(e=>e.text.toLowerCase().includes(query));
    if($('journal-sort').value==='oldest')sorted.reverse();
    $('all-reflections').innerHTML=sorted.length?sorted.map(entryMarkup).join(''):'<div class="empty"><p>No matching reflections yet.</p></div>';
    chart('activity-chart',entries,1,'journals');chart('score-chart',checkins,30,'checkins');
    document.querySelectorAll('[data-delete]').forEach(btn=>btn.addEventListener('click',async()=>{
      if(!confirm('Permanently delete this reflection?'))return;
      const id=btn.dataset.delete;
      try{if(authenticated()){await api('journals/'+encodeURIComponent(id)+'/','DELETE');await loadRemote()}
        else{local.journals=local.journals.filter(x=>String(x.id)!==id);saveLocal();state=local;render()}toast('Reflection deleted.')}
      catch(e){toast(e.message)}
    }));
  }
  $('journal-search').addEventListener('input',render);$('journal-sort').addEventListener('change',render);
  $('export-data').addEventListener('click',()=>{
    const out={version:3,mode:authenticated()?'cloud':'browser-demo',exported_at:new Date().toISOString(),journals:state.journals,checkins:state.checkins};
    const blob=new Blob([JSON.stringify(out,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),link=document.createElement('a');
    link.href=url;link.download='mental-health-detector-data.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);toast('Your data was exported.');
  });
  $('clear-data').addEventListener('click',async()=>{
    if(!confirm(authenticated()?'Delete all your cloud journal entries and check-ins? This cannot be undone. Your account will remain.':'Delete all your browser-demo entries? This cannot be undone.'))return;
    try{if(authenticated()){await api('my-data/','DELETE');await loadRemote()}
      else{localStorage.removeItem(KEY);local=blank();state=local;render()}toast('All entries were deleted.');go('overview')}
    catch(e){toast(e.message)}
  });
  $('import-demo').addEventListener('click',async()=>{
    if(!authenticated()){toast('Sign in first.');return}
    const count=local.journals.length+local.checkins.length;
    if(!count){toast('No demo entries to import.');return}
    if(!confirm(`Upload ${count} browser-demo entries to your cloud account? This is optional and cannot be undone automatically.`))return;
    if(busy)return;busy=true;let imported=0;
    try{for(const x of local.journals){await api('journals/','POST',{text:x.text,mood:x.mood||null});imported++}
      for(const x of local.checkins){await api('checkins/','POST',{answers:x.answers||x.values});imported++}
      await loadRemote();toast(`${imported} entries imported. Your browser-demo data was left unchanged.`);
    }catch(e){toast(`${imported} imported; remaining entries were not uploaded. ${e.message}`)}finally{busy=false}
  });
  async function init(){
    try{const response=await fetch('/api/config/',{cache:'no-store'});if(!response.ok)throw Error('config unavailable');const config=await response.json();
      cloudReady=!!(config.cloud_enabled&&config.url&&config.publishable_key&&window.supabase?.createClient);
      if(cloudReady){cloud=window.supabase.createClient(config.url,config.publishable_key,{auth:{autoRefreshToken:true,persistSession:true,detectSessionInUrl:true}});
        const {data}=await cloud.auth.getUser();user=data?.user||null;
        cloud.auth.onAuthStateChange((event,session)=>{
          if(event==='SIGNED_OUT'){user=null;state=local;setMode();render()}
          else if((event==='SIGNED_IN'||event==='TOKEN_REFRESHED')&&session?.user){
            const changed=!user||user.id!==session.user.id;user=session.user;setMode();if(changed){state=blank();queueMicrotask(loadRemote)}
          }
        });
        if(user){state=blank();await loadRemote()}
      }
    }catch(e){console.warn('Cloud connection unavailable; browser demo remains functional.')}
    setMode();render();
  }
  init();
})();
