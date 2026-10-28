
document.querySelectorAll('.card').forEach(card=>{
  card.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{card.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x===b));card.querySelectorAll('.view').forEach(v=>v.classList.toggle('on',v.classList.contains(b.dataset.v)));});
  const s=card.querySelector('.slider');s.oninput=()=>{card.querySelectorAll('.curtain .top,.curtain .bar').forEach(e=>e.style.setProperty('--x',s.value+'%'));};
  const bl=card.querySelector('.view.blink'),au=card.querySelector('.auto'),op=card.querySelector('.op'),b=bl.querySelector('.b');
  const sync=()=>{bl.classList.toggle('auto-on',au.checked);b.style.opacity=au.checked?'':op.value/100;};au.onchange=sync;op.oninput=()=>{au.checked=false;sync();};sync();
  const g=card.querySelector('.showgrid');g.onchange=()=>card.querySelector('.grid').classList.toggle('off',!g.checked);
});
