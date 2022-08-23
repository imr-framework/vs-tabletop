$('#link-to-game1').addClass('text-success');

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
});
$(document).ready(function(){
  $('[data-bs-toggle="popover"]').popover();
});

let socket = io();

$(':input').on('change', (event)=>{
    console.log('Updating')
    socket.emit("Update param for Game1", {'id': event.target.id, 'value': event.target.value});
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
        $(`#mc-failure-text-${q_ind}`).addClass('d-none');
        $(`#mc-success-text-${q_ind}`).removeClass('d-none')
        socket.emit('game 1 question answered',{'ind': q_ind, 'correct': true});
    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-failure-text-${q_ind}`).removeClass('d-none');
        $(`#mc-success-text-${q_ind}`).addClass('d-none')
        // Hide success text
        socket.emit('game 1 question answered',{'ind': q_ind, 'correct': false});
    }


    //choice="some choice"
    console.log('Updating choice')
    //socket.emit("Updating choice for Game 1", {'choice':choice});
})



$('.tabs__toggle').on('click', (event)=>{
    console.log('reset')
    $('#Matrix_scale').val(128);
    $('#Voxel_scale').val(1.00);
    $('#FOV_scale').val(128.00);
    $('#zero_fill').val(128);
    socket.emit('Reset param for Game1')
    console.log('Reset request sent')

})

socket.on('G1 take session data', (msg)=>{
    console.log('I am supposed to be updating data')
    $('#Matrix_scale').val(msg['data']['Matrix_scale']);
    $('#Voxel_scale').val(msg['data']['Voxel_scale']*1000);
    $('#FOV_scale').val(msg['data']['FOV_scale']*1000);
    $('#zero_fill').val(msg['data']['zero_fill']);
    $('#Min_scale').val(msg['data']['Min_scale']);
    $('#Max_scale').val(msg['data']['Max_scale']);
    console.log(msg['data'])
})



function controlFromInput(fromSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#25daa5', controlSlider);
    if (from > to) {
        fromSlider.value = to;
        fromInput.value = to;
    } else {
        fromSlider.value = from;
    }
    if(from < 0){
        fromInput.value = 0
    }
    if(to > 100){
        toInput.value = 100
    }
}

function controlToInput(toSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#25daa5', controlSlider);
    setToggleAccessible(toInput);
    if (from <= to) {
        toSlider.value = to;
        toInput.value = to;
    } else {
        toInput.value = from;
    }
}

function controlFromSlider(fromSlider, toSlider, fromInput, toInput) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
  if (from > to) {
    fromSlider.value = to;
    fromInput.value = to;
  } else {
    fromInput.value = from;
  }

  if(from < 0){
        fromInput.value = 0
    }



}

function controlToSlider(fromSlider, toSlider, toInput) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
  setToggleAccessible(toSlider);
  if (from <= to) {
    toSlider.value = to;
    toInput.value = to;
  } else {
    toInput.value = from;
    toSlider.value = from;
  }
  if(to > 100){
    console.log(toInput.value)
    toInput.value = 100
  }
  if(toInput.value > 100){
    toInput.value = 100
  }

}

function getParsed(currentFrom, currentTo) {
  const from = parseInt(currentFrom.value, 10);
  const to = parseInt(currentTo.value, 10);
  return [from, to];
}

function fillSlider(from, to, sliderColor, rangeColor, controlSlider) {
    const rangeDistance = to.max-to.min;
    const fromPosition = from.value - to.min;
    const toPosition = to.value - to.min;
    controlSlider.style.background = `linear-gradient(
      to right,
      ${sliderColor} 0%,
      ${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,
      ${rangeColor} ${((fromPosition)/(rangeDistance))*100}%,
      ${rangeColor} ${(toPosition)/(rangeDistance)*100}%,
      ${sliderColor} ${(toPosition)/(rangeDistance)*100}%,
      ${sliderColor} 100%)`;
}

function setToggleAccessible(currentTarget) {
  const toSlider = document.querySelector('#toSlider');
  if (Number(currentTarget.value) <= 0 ) {
    toSlider.style.zIndex = 2;
  } else {
    toSlider.style.zIndex = 0;
  }
}

const fromSlider = document.querySelector('#fromSlider');
const toSlider = document.querySelector('#toSlider');
const fromInput = document.querySelector('#fromInput');
const toInput = document.querySelector('#toInput');
fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
setToggleAccessible(toSlider);

fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromInput, toInput);
toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toInput);
fromInput.oninput = () => controlFromInput(fromSlider, fromInput, toInput, toSlider);
toInput.oninput = () => controlToInput(toSlider, fromInput, toInput, toSlider);



socket.on('Recreate Image', (payload)=>{
    j1 = JSON.parse(payload['data']);
    Plotly.newPlot('chart-G1', j1, {})
})




socket.on('renew stars',(msg)=>{
    console.log('Stars should be updated now...')
    num_stars = msg['stars'];
    num_full = parseInt(Math.floor(num_stars));
    num_half = parseInt(Math.round((num_stars-num_full)*2));
    num_empty = 5 - num_full - num_half;


    let stars_html = ''
    stars_html += '<i class="bi bi-star-fill text-warning"></i> '.repeat(num_full)
    stars_html += '<i class="bi bi-star-half text-warning"></i> '.repeat(num_half)
    stars_html += '<i class="bi bi-star text-warning"></i> '.repeat(num_empty)

    $("#stars-display").html(stars_html);
})

socket.on("Reset Matrix Scale", (msg)=>{
    $('#Matrix_scale').val(128);
    $('#zero_fill').val(128);
    socket.emit("Done Resetting Matrix Scale")
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

