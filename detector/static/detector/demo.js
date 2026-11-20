/* Mindful Space: browser demo plus Supabase Auth / Django API-backed private accounts. */
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
  const saveLocal=()=>{try{localStorage.setItem(KEY,JSON.stringify(local));return true}catch(_){toast('Browser storage is unavailable. Your changes may not persist¶»§q«^