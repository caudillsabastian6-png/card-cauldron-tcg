/* Creatures v1: pet icon picker + Bubblet helper. Static preview: helper answers are scripted. */
(function(){
  "use strict";
  var PETS=[["emberwyrm","Emberwyrm","baby dragon"],["zapkit","Zapkit","spark critter"],["cinderclaw","Cinderclaw","fire drake"],
            ["bubblet","Bubblet","potion slime"],["frostfin","Frostfin","ice swimmer"],["mosspup","Mosspup","leaf pup"]];
  var key="ror.pet", cur=localStorage.getItem(key)||"emberwyrm";
  function src(id){return "pets/"+id+".webp";}
  function paint(){document.querySelectorAll(".pet img").forEach(function(i){i.src=src(cur);});}
  function sheet(html){
    var s=document.createElement("div");s.className="sheet-scrim";var p=document.createElement("div");p.className="sheet";p.setAttribute("role","dialog");
    p.innerHTML='<div class="grab"></div>'+html;document.body.appendChild(s);document.body.appendChild(p);
    requestAnimationFrame(function(){s.classList.add("open");p.classList.add("open");});
    function close(){s.classList.remove("open");p.classList.remove("open");setTimeout(function(){s.remove();p.remove();},300);}
    s.onclick=close;document.addEventListener("keydown",function k(e){if(e.key==="Escape"){close();document.removeEventListener("keydown",k);}});
    return {el:p,close:close};
  }
  function picker(){
    var h='<h3>Pick your pet</h3><p class="sub">Your pet is your icon everywhere in the app.</p><div class="petgrid">'+
      PETS.map(function(p){return '<button class="petopt" type="button" data-p="'+p[0]+'" aria-pressed="'+(p[0]===cur)+'"><img src="'+src(p[0])+'" alt=""><b>'+p[1]+'</b><small>'+p[2]+'</small></button>';}).join("")+'</div>';
    var s=sheet(h);
    s.el.querySelectorAll(".petopt").forEach(function(b){b.onclick=function(){cur=b.dataset.p;localStorage.setItem(key,cur);
      s.el.querySelectorAll(".petopt").forEach(function(x){x.setAttribute("aria-pressed",x===b);});paint();setTimeout(s.close,350);};});
  }
  var A={
    check:"Tap the gold Check button, line the front of your card up inside the outline, and press the picture button. You'll get the market price on every scan.",
    coins:"You earn coins by playing games and daily bonuses. Spend them in the shop or pour them into the Donation Cauldron to help send packs to kids in the hospital.",
    binders:"Binders are your collection. Tap Binders at the bottom to see every card you've checked, sorted into binders you name.",
    cauldron:"The Donation Cauldron is where you pour coins. When the pot fills, real sealed packs go to kids in the hospital.",
    friends:"Open Invite friends in the menu. Share your link with a tap, and you both get coins when they join and play.",
    broken:"Sorry about that! Tell me what happened in a few words and I'll pass it straight to the team.",
    lost:"No worries, I've got you. What were you trying to do? You can tap one of the buttons above or just type it."
  };
  function answer(q){q=q.toLowerCase();
    if(/check|scan|photo|picture|camera|fake|real/.test(q))return A.check;
    if(/coin|earn|shop/.test(q))return A.coins;
    if(/binder|collection|my cards/.test(q))return A.binders;
    if(/donat|cauldron|kid|hospital/.test(q))return A.cauldron;
    if(/friend|refer|invite/.test(q))return A.friends;
    if(/broke|bug|crash|wrong|not work/.test(q))return A.broken;
    return A.lost;}
  function helper(){
    var s=sheet('<div class="bothead"><img src="pets/bubblet.webp" alt=""><div><h3>Hi, I\'m Bubblet!</h3><p class="sub" style="margin:0">Lost? Ask me anything about the app.</p></div></div>'+
      '<div class="chips"><button data-q="check">Check a card</button><button data-q="coins">Coins</button><button data-q="binders">My binders</button><button data-q="cauldron">Donations</button><button data-q="friends">Invite friends</button><button data-q="broken">Something broke</button></div>'+
      '<div class="chat" id="chat"><div class="msg bot">Hey! What can I help you find?</div></div>'+
      '<form class="ask"><input placeholder="Type your question" aria-label="Your question"><button>Ask</button></form>');
    var chat=s.el.querySelector("#chat");
    function say(t,who){var m=document.createElement("div");m.className="msg "+who;m.textContent=t;chat.appendChild(m);chat.scrollTop=chat.scrollHeight;}
    s.el.querySelectorAll(".chips button").forEach(function(b){b.onclick=function(){say(b.textContent,"me");setTimeout(function(){say(A[b.dataset.q],"bot");},350);};});
    s.el.querySelector("form").onsubmit=function(e){e.preventDefault();var i=this.querySelector("input");if(!i.value.trim())return;say(i.value,"me");var a=answer(i.value);i.value="";setTimeout(function(){say(a,"bot");},350);};
    var dot=document.querySelector(".helper .dot");if(dot)dot.remove();
  }
  document.querySelectorAll("[data-pet-picker]").forEach(function(b){b.addEventListener("click",function(e){e.stopPropagation();location.href="pet.html";});});
  var h=document.createElement("button");h.className="helper";h.type="button";h.setAttribute("aria-label","Ask Bubblet for help");
  h.innerHTML='<img src="pets/bubblet.webp" alt=""><span class="dot"></span>';h.onclick=helper;document.body.appendChild(h);
  paint();
})();
