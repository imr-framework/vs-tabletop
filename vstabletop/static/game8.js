let socket = io();


$('#link-to-game8').addClass('text-success');

$('#mode-2d').on('click',()=>{
    $('#mystery-image-3d').addClass('d-none');
    $('#prescription-3d').addClass('d-none');
    $('#3d-images-card').addClass('d-none');

    $("#mystery-image-2d").removeClass('d-none');
    $('#prescription-2d').removeClass('d-none');
    $('#2d-images-card').removeClass('d-none');

    socket.emit('Draw new 2D image');
})

$('#mode-3d').on('click',()=>{
    $("#mystery-image-3d").removeClass('d-none');
    $('#prescription-3d').removeClass('d-none');
    $('#3d-images-card').removeClass('d-none');

    $('#mystery-image-2d').addClass('d-none');
    $('#prescription-2d').addClass('d-none');
    $('#2d-images-card').addClass('d-none');
    socket.emit('Draw new 3D model');
})

$('#image-1d').on('click',()=>{
    socket.emit("Get 1D projection",{'angle':$('#proj1d_angle').val()});
})

$('#image-2d').on('click',()=>{
    let axis;
    $('.proj-2d-xyz').each(function(){
        console.log($(this)[0].checked);
        if ($(this)[0].checked){
            axis = $(this).val();
        }
    })
    socket.emit("Get 2D projection",{'axis': axis});

})

socket.on("Deliver options plot", (payload)=>{
    Plotly.newPlot('game8-choices-chart',JSON.parse(payload['graph']), {autosize: true});
})

socket.on("Message",(message)=>{
    $("#message-region").text(message['text']);
})


$(':input').on('change', (event)=>{
    socket.emit("Update parameter for game 8", {'id': event.target.id, 'value': event.target.value});
})

//'Deliver attempt plot', {'mode': '3D', 'graph': j1, 'attempt': num_attempts_sofar + 1
socket.on("Deliver attempt plot",(payload)=>{
    switch_to_tab(payload);
    setTimeout(() => {
         if (payload['mode'] === '3D'){
        Plotly.newPlot(`chart-3d-attempt${payload['attempt']}`, JSON.parse(payload['graph']), {autosize: true});
        console.log(`Attempt #${payload['attempt']}`);

        }
        else if (payload['mode'] === '2D'){
            Plotly.newPlot(`chart-2d-attempt${payload['attempt']}`, JSON.parse(payload['graph']), {autosize: true});

        }
    }, 500);


})

$('#reset-button').on('click',()=>{
    socket.emit("Reset attempts without changing question");
})

socket.on('Wipe all attempt plots',()=>{
    $('.chart-attempt').each(function(){
        Plotly.purge($(this).attr('id'));
    })
    $("#feedback-correct").addClass('d-none');
    $("#feedback-wrong").addClass('d-none');
    //$("#submit-button").attr('disabled',false);
    $('.submit-option').attr('disabled',false).prop('checked',false);
})

$("#new-model-button").on('click',()=>{
    console.log("New model requested");
    if ($('#2d-images-card').hasClass("d-none")){
        socket.emit('Draw new 3D model');
    }
    else{
        socket.emit("Draw new 2D image");
    }
})

$('.submit-option').on('click',()=>{
    $('#submit-button').attr('disabled',false);
})

$('#submit-button').on('click',()=>{
    // Which answer was chosen?
    let choice;
    $('.submit-option').each(function(){
        console.log($(this)[0].checked);
        if ($(this)[0].checked){
            choice = $(this).val();
        }
        $(this).attr('disabled',true);
    })
    socket.emit("Answer submitted",{'choice':choice})
    // Disable submit button
    $('#submit-button').attr('disabled',true);

})

socket.on("Correct",()=>{
    $("#feedback-correct").removeClass('d-none');
    $("#feedback-wrong").addClass('d-none');
})

socket.on("Wrong",()=>{
    $("#feedback-correct").addClass('d-none');
    $("#feedback-wrong").removeClass('d-none');
})

function switch_to_tab(payload){
    const someTabTriggerEl = document.querySelector(`#game8-${payload['mode'].toLowerCase()}-tab-${payload['attempt']-1}`);
    const tab = new mdb.Tab(someTabTriggerEl);
    tab.show();
}



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
        $(`#mc-failure-text-${q_ind}`).addClass('d-none');
        $(`#mc-success-text-${q_ind}`).removeClass('d-none')
        socket.emit('game 8 question answered',{'ind': q_ind, 'correct': true});
    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-failure-text-${q_ind}`).removeClass('d-none');
        $(`#mc-success-text-${q_ind}`).addClass('d-none');
        // Hide success text
        socket.emit('game 8 question answered',{'ind': q_ind, 'correct': false});
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


// Progress tracking
$(".task-next-button").click((event)=>{
    let task_id = event.target.id.replace('task','').replace('-next','');
    // Check if all checkboxes of task are selected
    if ($(`input.task-${task_id}-check`).not(':checked').length === 0){
        console.log('All boxes are checked! Moving on.')
        // Update session progress
            socket.emit('game8 update progress',{'task': task_id});
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
    if (step * 100/3 > current) {
        $('.progress-bar').prop('style', `width: ${step * 100/3}%`).prop('aria-valuenow', `${step * 100/3}`);
    }
}

function go_to_next_tab(step) {
    if (step < 3) {
        $(`#task${step + 1}-tab`).removeClass('disabled');
        $(`#task${step + 1}-tab`).tab('show');
        $(`#step${step}`).removeClass('show active');
        $(`#step${step + 1}`).addClass('show active');
        // Change to default parameters for that task
    }
}



