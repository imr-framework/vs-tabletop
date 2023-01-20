// New version: don't rely on forms
let socket = io();

$('#game1-run').on('click',()=>{
    // Check validity of inputs
    // FOV

    fov = parseFloat($('#FOV_scale').val());
    n = parseInt($('#Matrix_scale').val());
    zf = parseInt($('#zero_fill').val());


    console.log(n);
    console.log(zf);

    let all_valid = true;
    if (fov > 2500 || fov < 50){
        all_valid = false;
        // Display warning
        $('#FOV_scale').addClass('is-invalid');
        $('#fovhelp').removeClass('d-none');

    }
    else{
        $('#FOV_scale').removeClass('is-invalid');
        $('#fovhelp').addClass('d-none');

    }

    if (n>1000 || n<8){
        all_valid = false;
        // Display warning
        $('#Matrix_scale').addClass('is-invalid');
        $('#matrixsizehelp').removeClass('d-none');
    }
    else{
        $('#Matrix_scale').removeClass('is-invalid');
        $('#matrixsizehelp').addClass('d-none');

    }
    if (zf>1200 || zf<8){
        all_valid = false;
        // Display warning
        $('#zero_fill').addClass('is-invalid');
        $('#zerofillhelp').removeClass('d-none');
    }
    else{
        $('#zero_fill').removeClass('is-invalid');
        $('#zerofillhelp').addClass('d-none');

    }

    if (all_valid){

        // Disable button
        $('#game1-run').attr('disabled',true);
        $('#game1-spinner').removeClass('d-none');
        socket.emit('Acquire game 1 image',{'fov': fov,
                                            'n':n,
                                            'zerofill': zf,
                                            'window_min': parseFloat($('#fromSlider').val()),
                                            'window_max': parseFloat($('#toSlider').val())});
        // Check off the task if conditions are satisfied (base on which latest step we are on)
        // Find current step
        let current_step = 4;
        for (let step = 2; step <=4 ; step++) {
            if ($(`#task${step}-tab`).hasClass('disabled')){
                current_step = step - 1;
                break;
            }
        }
        console.log(`Current step: ${current_step}`);

        if (current_step === 1){
            let fov = parseFloat($('#FOV_scale').val());
            if (fov >= 230 && fov <= 300){
                // Check off Task 1
                $('#final-task-of-1').prop('checked',true);
            }
        }
        else if (current_step === 2){
            let n = parseInt($('#Matrix_scale').val());
            if (n>=256){
                $('#final-task-of-2').prop('checked',true);
            }
        }
        else if (current_step === 3){
            let n = parseInt($('#Matrix_scale').val());
            let zf = parseInt($('#zero_fill').val());
            if (n <= 32 && zf >= 256){
                $('#final-task-of-3').prop('checked',true);
            }
        }
        else if (current_step === 4){
            let window_min = parseFloat($('#fromSlider').val());
            let window_max = parseFloat($('#toSlider').val());
            if (window_min >= 60 && window_max > 60){
                $('#final-task-of-4').prop('checked',true);
            }
        }

    }
})

socket.on('Deliver image',(payload)=>{
    console.log("Image delivered")
    graphData = JSON.parse(payload['graphData']);
    Plotly.newPlot('chart-G1',graphData);

    $('#game1-run').attr('disabled',false);
    $('#game1-spinner').addClass('d-none');
})


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


$(':input').on('change', (event)=>{
    console.log('Updating')
    socket.emit("Update param for Game1", {'id': event.target.id, 'value': event.target.value});
})


// Tasks / progress

$(".task-next-button").click((event)=>{
    let task_id = event.target.id.replace('task','').replace('-next','');
    // Check if all checkboxes of task are selected
    if ($(`input.task-${task_id}-check`).not(':checked').length === 0){
        console.log('All boxes are checked! Moving on.')
        // Update session progress
            socket.emit('game1 update progress',{'task': task_id});
            $(`#task-message-${task_id}`).addClass('d-none');
            $(`#task-success-${task_id}`).removeClass('d-none');
            update_progress_bar(task_id);
            go_to_next_tab(parseInt(task_id));

    }
    else{
        // If this task hasn't been completed, print hint
        // Use tab active status to judge
        if (parseInt(task_id) === 4 || $(`#task${parseInt(task_id)+1}-tab`).hasClass('disabled')){
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
    if (step * 25 > current) {
        $('.progress-bar').prop('style', `width: ${step * 25}%`).prop('aria-valuenow', `${step * 25}`);
    }
}

function go_to_next_tab(step){
    if (step<4){
        $(`#task${step+1}-tab`).removeClass('disabled');
        $(`#task${step+1}-tab`).tab('show');
        $(`#step${step}`).removeClass('show active');
        $(`#step${step+1}`).addClass('show active');
        // Change to default parameters for that task
        change_to_default_params(step+1);
    }
    else{
        // Play confetti
        loop();
    }
}

function change_to_default_params(step){
    if (step === 1){
            $('#Matrix_scale').val(128);
            $('#Voxel_scale').val(1);
            $('#FOV_scale').val(128);
            $('#zero_fill').val(128);
            $('#Min_scale').val(10);
            $('#Max_scale').val(90);
    }
    else if (step === 2){
            $('#Matrix_scale').val(128);
            $('#Voxel_scale').val(250/128);
            $('#FOV_scale').val(250);
            $('#zero_fill').val(128);
            $('#Min_scale').val(10);
            $('#Max_scale').val(90);
    }
    else if (step === 3){
            $('#Matrix_scale').val(128);
            $('#Voxel_scale').val(1);
            $('#FOV_scale').val(128);
            $('#zero_fill').val(128);
            $('#Min_scale').val(0);
            $('#Max_scale').val(100);
    }
    else if (step === 4){
            $('#Matrix_scale').val(256);
            $('#Voxel_scale').val(1);
            $('#FOV_scale').val(256);
            $('#zero_fill').val(256);
            $('#Min_scale').val(0);
            $('#Max_scale').val(100);
    }
}

$('.task_tab').on('click',(event)=>{
    // Find which task it is
    step = event.target.id[4];
    // Update parameters
    change_to_default_params(parseInt(step));
})


$('.answer-mc').on('click', (event)=>{
    submit_id = event.target.id;
    q_ind = submit_id[submit_id.length-1]
    console.log(submit_id);

    console.log($('.q0-choice:checked'));

    choice = $(`.q${q_ind}-choice:checked`).last().attr("value");

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

