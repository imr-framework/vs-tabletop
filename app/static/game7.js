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
$('#randomize').click(()=>{
    // TODO get random 3D model.
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
    }
}
