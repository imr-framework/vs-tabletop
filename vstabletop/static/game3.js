let socket = io();

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
        $(`#mc-failure-text-${q_ind}`).addClass('d-none');
        $(`#mc-success-text-${q_ind}`).removeClass('d-none')
        socket.emit('game 3 question answered',{'ind': q_ind, 'correct': true});
    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-failure-text-${q_ind}`).removeClass('d-none');
        $(`#mc-success-text-${q_ind}`).addClass('d-none');
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

    let stars_html = '';
    stars_html += '<i class="bi bi-star-fill text-warning"></i> '.repeat(num_full);
    stars_html += '<i class="bi bi-star-half text-warning"></i> '.repeat(num_half);
    stars_html += '<i class="bi bi-star text-warning"></i> '.repeat(num_empty);

    $("#stars-display").html(stars_html);
})
//
// const canvasEl = document.querySelector('#canvas');
//
// const w = canvasEl.width = window.innerWidth;
// const h = canvasEl.height = window.innerHeight * 2;

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
//
// const ctx = canvasEl.getContext('2d');
// const confNum = Math.floor(w / 4);
// const confs = new Array(confNum).fill().map(_ => new Confetti());
//
// loop();


socket.on('G3 take session data', (msg)=>{
    console.log('Updating g3 data')
    $('#options').val(msg['data']['options']);
    $('#TR').val(msg['data']['TR']);
    $('#TE').val(msg['data']['TE']);
    $('#FA').val(msg['data']['FA']);
    console.log(msg['data'])
 })
//
// $('.carousel').carousel({
//   interval: false,
// });


$('#game3-run').on('click',()=>{
    // Get settings
    console.log('Requesting image');
    socket.emit('Game 3 acquire image',{'TR': parseFloat($('#TR').val()),
                                        'TE': parseFloat($('#TE').val()),
                                        'FA': parseFloat($('#FA').val())});


})


socket.on('Deliver image',(payload)=>{
    console.log("Image delivered")
    graphData1 = JSON.parse(payload['graphData1']);
    graphData2 = JSON.parse(payload['graphData2']);

    Plotly.newPlot('chart-G3',graphData1);
    Plotly.newPlot('chart-G3-bar',graphData2)
    $('#game3-run').attr('disabled',false);
    $('#game3-spinner').addClass('d-none');

     let current_step = 3;
     for (let step = 2; step <=3 ; step++) {
         if ($(`#task${step}-tab`).hasClass('disabled')){
             current_step = step - 1;
             break;
         }
     }
    console.log(`Current step: ${current_step}`);
    if (payload[`task${current_step}_pass`]===1){
        $(`#final-task-of-${current_step}`).prop('checked',true);
    }

})

// Instant value display
$("#TR").on('change',()=>{
    $('#TR-val').text($('#TR').val());
})

$("#TE").on('change',()=>{
    $('#TE-val').text($('#TE').val());
})

$("#FA").on('change',()=>{
    $('#FA-val').text($('#FA').val());
})




// Progress tracking
$(".task-next-button").click((event)=>{
    let task_id = event.target.id.replace('task','').replace('-next','');
    // Check if all checkboxes of task are selected
    if ($(`input.task-${task_id}-check`).not(':checked').length === 0){
        console.log('All boxes are checked! Moving on.')
        // Update session progress
            socket.emit('game3 update progress',{'task': task_id});
            $(`#task-message-${task_id}`).addClass('d-none');
            $(`#task-success-${task_id}`).removeClass('d-none');
            update_progress_bar(task_id);
            go_to_next_tab(parseInt(task_id));

    }
    else{
        // If this task hasn't been completed, print hint
        // Use tab active status to judge
        if (parseInt(task_id) === 3 || $(`#task${parseInt(task_id)+1}-tab`).hasClass('disabled')){
            console.log('showing hint message')
            console.log(`#task-message-${task_id}`);
            $(`#task-message-${task_id}`).removeClass('d-none');

        }
        else{ // If step is already completed, just go to the next tab.
            go_to_next_tab(parseInt(task_id));
            // For the last step, display final success image
        }
    }
})

function update_progress_bar(step) {
    // Update progress bar only if new value is larger than existing value.
    let current = parseInt($('.progress-bar').attr('style').replace('width: ', '').replace('%', ''));
    if (step * (100/3) > current) {
        $('.progress-bar').prop('style', `width: ${step * 100/3}%`).prop('aria-valuenow', `${step * 100/3}`);
    }
}

function go_to_next_tab(step){
    if (step<3){
        $(`#task${step+1}-tab`).removeClass('disabled');
        $(`#task${step+1}-tab`).tab('show');
        $(`#step${step}`).removeClass('show active');
        $(`#step${step+1}`).addClass('show active');
        // Change to default parameters for that task
    }




}