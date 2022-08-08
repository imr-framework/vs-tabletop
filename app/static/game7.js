let socket = io();
let layout = {autosize: true};

$(':input').on('change', (event)=>{
    socket.emit("Update param for Game7", {'id': event.target.id, 'value': event.target.value});
})



$('#button-3d-model').on('click',()=>{
    socket.emit("Request 3D model")
})

$('#button-2d-proj').on('click',()=>{
    socket.emit("Request 2D projection")
})

$('#button-1d-proj').on('click',()=>{
    socket.emit("Request 1D projection")
})

$('#lines-toggle').on('click',()=>{
    socket.emit("Toggle line display")
})

$('.proj-2d-xyz').on('input',(event)=>{
    socket.emit("Update line direction",{'dir': event.target.value});

})



socket.on('Deliver 3D model', (payload)=>{
    graphData1 = JSON.parse(payload['graph1'])
    graphData2 = JSON.parse(payload['graph2'])
    graphData3 = JSON.parse(payload['graph3'])
    Plotly.newPlot('chart-G7-3D',graphData1,layout)
    Plotly.newPlot('chart-G7-2D',graphData2,layout)
    Plotly.newPlot('chart-G7-1D',graphData3,layout)
})

socket.on('Deliver 2D projection', (payload)=>{
    graphData = JSON.parse(payload['graph']);
    Plotly.newPlot('chart-G7-2D',graphData,layout)
})

socket.on('Deliver 1D projection', (payload)=>{
    graphData = JSON.parse(payload['graph']);
    Plotly.newPlot('chart-G7-1D',graphData,layout)

})



// Enable question mark popovers
$(document).ready(function(){
  $('[data-bs-toggle="popover"]').popover();
});

// Multiple choice
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
        $(`#mc-failure-text-${q_ind}`).addClass('d-none')
        socket.emit('game 7 question answered',{'ind':q_ind, 'correct':true});

    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-success-text-${q_ind}`).addClass('d-none')
        $(`#mc-failure-text-${q_ind}`).removeClass('d-none')
        socket.emit('game 7 question answered',{'ind':q_ind,'correct':false});

        // Hide success text
    }
    console.log('Updating choice')
})


socket.on('renew stars',(msg)=>{
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

// Task completion tracking
$(".task-next-button").click((event)=>{
    let task_id = event.target.id.replace('task','').replace('-next','');
    // Check if all checkboxes of task are selected
    if ($(`input.task-${task_id}-check`).not(':checked').length === 0){
        console.log('All boxes are checked! Moving on.')
        // Update session progress
        socket.emit('game7 update progress',{'task': task_id});
        $(`#task-message-${task_id}`).addClass('d-none');
        $(`#task-success-${task_id}`).removeClass('d-none');
        update_progress_bar(task_id);
        go_to_next_tab(parseInt(task_id));

    }
    else{
        // If this task hasn't been completed, print hint
        // Use tab active status to judge
        if (parseInt(task_id) === 4 || $(`#task${parseInt(task_id)+1}-tab`).hasClass('disabled')){
            console.log(`#task-message-${task_id}`);
            $(`#task-message-${task_id}`).removeClass('d-none');

        }
        else{ // If step is already completed, just go to the next tab.
            go_to_next_tab(parseInt(task_id));
            // For the last step, display final success image
        }
    }
})

// Interactive task - generate random initial and target M's!
$('.randomize').click((event)=>{
    // TODO get random 3D model.
    let t = '2D';

    if (event.target.id === 'randomize-2'){
        t = '1D';
    }

    socket.emit('Pull random model',{'type':t})


})

let correct_ind_1d = -1
let correct_ind_2d = -1

socket.on('display new challenge',(msg)=>{
    console.log('I am supposed to be renewing the images now')
    correct_ind_2d = msg['corr_2d'];
    correct_ind_1d = msg['corr_1d'];
    $('#image-opts').removeClass('d-none');
    $('#image-opts-2').removeClass('d-none');

    $('#challenge-info-2d').text(`The projection axis is ${msg['axis']}`);
    $('#challenge-info-1d').text(`The projection angle is ${msg['angle']}`);

    for (u=0;u<3;u++){
        insert_image_2d(u);
        $(`#task-img-2d-${u}`).removeAttr('src').attr('src',`../static/img/game7/im2d-${u}.jpg?t=` + new Date().getTime());

        insert_image_1d(u);
        $(`#task-img-1d-${u}`).removeAttr('src').attr('src',`../static/img/game7/im1d-${u}.jpg?t=` + new Date().getTime());

    }

    if (msg['type'] === '1D'){
        $('#button-2d-proj').trigger('click');
    }


    function insert_image_2d(u) {
        const element = document.getElementById(`task-img-2d-${u}`);
        if (!element) {
            let img = document.createElement('img');
            img.src = `../static/img/game7/im2d-${u}.jpg?t=` + new Date().getTime();
            img.id = `task-img-2d-${u}`;
            $(`#img2d-label-${u}`).append(img);
        }
    }

    function insert_image_1d(u){
        const element2 = document.getElementById(`task-img-1d-${u}`);
        if (!element2){
            let img = document.createElement('img');
            img.src = `../static/img/game7/im1d-${u}.jpg?t=` + new Date().getTime();
            img.id = `task-img-1d-${u}`;
            img.width = 100;
            $(`#img1d-label-${u}`).append(img);
        }
    }




    // Refresh each of the 3 images
    //
    // for (u=0;u<3;u++) {
    //     remove_image_2d(u);
    //     setTimeout(200);
    //     insert_image_2d(u);
    // }
    //
    // function remove_image_2d(u){
    //     const element = document.getElementById(`task-img-2d-${u}`);
    //     if (element){
    //         console.log(element);
    //
    //         element.remove();
    //     }
    //     const e2 = document.getElementById(`task-img-2d-${u}`);
    //     console.log(e2);
    //
    // }
    //
    // function insert_image_2d(u){
    //     let img = document.createElement('img');
    //     img.src = `../static/img/game7/im2d-${u}.jpg`
    //     img.id = `task-img-2d-${u}`;
    //     $(`#img2d-label-${u}`).append(img);
    // }
    //
    // for (u = 1; u<4; u++){
    //     console.log(`renewing img ${u}`);
    //     url = $().attr("src");
    //     console.log(url);
    //     $(`#task-img-2d-${u}`)F.attr("src","");
    //     $(`#task-img-2d-${u}`).attr("src",url)
    // }




})

$('#check-answer-2d').click(()=>{
    let answer = -1;
    for (y=0;y<3;y++){
        if ($(`#choice_2d_${y}`).is(":checked")){
            answer = y;
        }
    }
    console.log(`Correct answer is ${correct_ind_2d} and you answered ${answer}`);

    if (answer===correct_ind_2d){
        $('#challenge-feedback-2d').text('Correct!').removeClass('text-warning').addClass('text-success');
    }
    else{
        $('#challenge-feedback-2d').text('Try again.').removeClass('text-success').addClass('text-warning');

    }

    $('#final-task-of-4').prop('checked',answer===correct_ind_2d);
})

$('#check-answer-1d').click(()=>{
    let answer = -1;
    for (x=0;x<3;x++){
        if ($(`#choice_1d_${x}`).is(":checked")){
            answer = x;
        }
    }
    console.log(`Correct answer for 1D is ${correct_ind_1d} and you answered ${answer}`);


    if (answer===correct_ind_1d){
        $('#challenge-feedback-1d').text('Correct!').removeClass('text-warning').addClass('text-success');
    }
    else{
        $('#challenge-feedback-1d').text('Try again.').removeClass('text-success').addClass('text-warning');

    }


    $('#final-task-of-5').prop('checked',answer===correct_ind_1d);
})



function update_progress_bar(step) {
    // Update progress bar only if new value is larger than existing value.
    let current = parseInt($('.progress-bar').attr('style').replace('width: ', '').replace('%', ''));
    if (step * 25 > current) {
        $('.progress-bar').prop('style', `width: ${step * 20}%`).prop('aria-valuenow', `${step * 20}`);
    }
}

function go_to_next_tab(step){
    if (step<5){
        $(`#task${step+1}-tab`).removeClass('disabled');
        $(`#task${step+1}-tab`).tab('show');
    }
    else{
        loop();
    }
}

$('.accordion-button.final-task-button').click((event)=>{
    let target = event.target.getAttribute('data-bs-target');
    let step = parseInt(target[target.length - 1]);
    if (step < 4){ // Step 3 does autocheck and it cannot be done by hand.
        $(`#final-task-of-${step}`).prop('checked',true);
    }

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

