$('#link-to-game3').addClass('text-success');


let tabs = document.querySelectorAll('.tabs__toggle'),
    contents = document.querySelectorAll('.tabs__content');

tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
        contents.forEach((content) => {
            content.classList.remove('is-active');
        });
        tabs.forEach((tab) => {
            tab.classList.remove('is-active');
        });
        contents[index].classList.add('is-active');
        tabs[index].classList.add('is-active');
    });
})

$(document).ready(function(){
  $('[data-bs-toggle="popover"]').popover();
})

let socket = io();

$(':input').on('change', (event)=>{
    socket.emit("Update param for Game3", {'id': event.target.id, 'value': event.target.value});
    console.log('in input')
})

$('.answer-mc').on('click', (event)=>{
    submit_id = event.target.id;
    q_ind = submit_id[submit_id.length-1]
    console.log(submit_id);
    choice = $(`.q${q_ind}-choice:checked`).attr("value");

    console.log(choice)

    let letters = ['a','b','c','d'];

    if (choice == letters[parseInt($(`#mc-correct-choice-${q_ind}`).text())]){
        console.log("Answer is correct! ")
        // Make success text visible
        $(`#mc-success-text-${q_ind}`).removeClass('d-none')
        socket.emit('game 3 question answered',{'ind': q_ind, 'correct': true});
    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-success-text-${q_ind}`).addClass('d-none')
        // Hide success text
        socket.emit('game 3 question answered',{'ind': q_ind, 'correct': false});
    }


    //choice="some choice"
    console.log('Updating choice')
})


socket.on('renew stars', (msg)=>{
    console.log('Stars should be updated now...')
    num_stars = msg['stars'];
    num_full = parseInt(Math.floor(num_stars));
    num_half = parseInt(Math.round((num_stars-num_full)*2));
    num_empty = 5 - num_full - num_half;

    let stars_html = `<span> ${num_stars} / 5 stars earned</span> `
    stars_html += '<i class="bi bi-star-fill"></i> '.repeat(num_full)
    stars_html += '<i class="bi bi-star-half"></i> '.repeat(num_half)
    stars_html += '<i class="bi bi-star"></i> '.repeat(num_empty)

    $("#stars-display").html(stars_html);
})

const canvasEl = document.querySelector('#canvas');

const w = canvasEl.width = window.innerWidth;
const h = canvasEl.height = window.innerHeight * 2;

function loop() {
  requestAnimationFrame(loop);
  ctx.clearRect(0,0,w,h);

  confs.forEach((conf) => {
    conf.update();
    conf.draw();
  })
}

function Confetti () {
  //construct confetti
  const colours = ['#fde132', '#009bde', '#ff6b00'];

  this.x = Math.round(Math.random() * w);
  this.y = Math.round(Math.random() * h)-(h/2);
  this.rotation = Math.random()*360;

  const size = Math.random()*(w/60);
  this.size = size < 15 ? 15 : size;

  this.color = colours[Math.floor(colours.length * Math.random())];

  this.speed = this.size/7;

  this.opacity = Math.random();

  this.shiftDirection = Math.random() > 0.5 ? 1 : -1;
}

Confetti.prototype.border = function() {
  if (this.y >= h) {
    this.y = h * 10;
  }
}

Confetti.prototype.update = function() {
  this.y += this.speed;

  if (this.y <= h) {
    this.x += this.shiftDirection/3;
    this.rotation += this.shiftDirection*this.speed/100;
  }

  if (this.y > h) this.border();
};

Confetti.prototype.draw = function() {
  ctx.beginPath();
  ctx.arc(this.x, this.y, this.size, this.rotation, this.rotation+(Math.PI/2));
  ctx.lineTo(this.x, this.y);
  ctx.closePath();
  ctx.globalAlpha = this.opacity;
  ctx.fillStyle = this.color;
  ctx.fill();
};

const ctx = canvasEl.getContext('2d');
const confNum = Math.floor(w / 4);
const confs = new Array(confNum).fill().map(_ => new Confetti());

loop();


socket.on('G3 take session data', (msg)=>{
    console.log('Updating g3 data')
    $('#options').val(msg['data']['options']);
    $('#TR').val(msg['data']['TR']);
    $('#TE').val(msg['data']['TE']);
    $('#FA').val(msg['data']['FA']);
    console.log(msg['data'])
})

$('.carousel').carousel({
  interval: false,
});


