(() => {
  const buttons=[...document.querySelectorAll('[data-preview-mood]')];
  const date=document.getElementById('landing-date');
  const next=document.getElementById('landing-continue');
  const feedback=document.getElementById('landing-feedback');
  if(!buttons.length||!next)return;
  if(date)date.textContent=new Intl.DateTimeFormat(undefined,{weekday:'long',month:'long',day:'numeric'}).format(new Date()).toUpperCase();
  let selected=null;
  const words={1:'A hard day deserves gentleness.',2:'It’s okay not to feel okay.',3:'A steady day is enough.',4:'It’s good to notice the bright moments.',5:'Make room for what feels good.'};
  buttons.forEach(btn=>btn.addEventListener('click',()=>{
    selected=Number(btn.dataset.previewMood);
    buttons.forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.previewMood)===selected)));
    feedback.textContent=words[selected]+' You can add this to a reflection.';
    next.textContent='Continue with this mood →';
  }));
  next.addEventListener('click',()=>{location.href='/demo/'+(selected?'?mood='+selected:'');});
})();
