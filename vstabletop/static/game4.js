// Initialize socket
let socket = io();

$('#link-to-game4').addClass('text-success');

$('#flow-manual-button').on("click",()=>{
    // Detect current mode
    let mode
    if ($('#flow-tab-1').hasClass('active')){
        mode = 'bright';
    }
    else{
        mode = 'dark';
    }
    // Change status
    if ($('#flow-manual-button').text() === 'PUSH'){
        $('#flow-manual-button').text('STOP').removeClass('btn-info').addClass('btn-danger');

        socket.emit('Flow on',{'mode':mode});
        console.log('flow on');
    }
    else{
        $('#flow-manual-button').text('PUSH').removeClass('btn-danger').addClass('btn-info');
        socket.emit('Flow off')
        // TODO stop animation frame

    }


})
//
// $('#flow_speed').on('change',()=>{
//     $('#flow-info').text(`Flow speed: ${20*$('#flow_speed').val()/100} mm / s`);
// })

$(':input').on('change', (event)=>{
    socket.emit("Update parameter for Game 4", {'id': event.target.id, 'value': event.target.value});
})

$('#T1').on('change',()=>{
    $('#t1-display').text($('#T1').val())
})

$('#T2').on('change',()=>{
    $('#t2-display').text($('#T2').val())
})

$('#flow-tab-1').on('click',()=>{
    socket.emit('Toggle mode',{'mode':'bright'})
    $('#contrast-type').val('bright');
    $('#fa-row').removeClass('d-none').show();
    $('#tr-row').removeClass('d-none').show();

    socket.emit("Update parameter for Game 4", {'id': 'contrast-type', 'value': 'bright'});
})

$('#flow-tab-2').on('click',()=>{
    socket.emit('Toggle mode',{'mode':'dark'})
    $('#contrast-type').val('dark');
    socket.emit("Update parameter for Game 4", {'id': 'contrast-type', 'value': 'dark'});
    $('#fa-row').hide();
    $('#tr-row').hide();
})

$('#contrast-type').on('input',(event)=>{
    let mode = event.target.value;
    if (mode === 'dark'){
        $('#flow-tab-1').removeClass('active');
        $('#flow-tab-2').addClass('active');
        $('#flow-tabs-1').removeClass('show active');
        $('#flow-tabs-2').addClass('show active')

        // Toggle input displays
        $('#fa-row').hide();
        $('#tr-row').hide();

    }
    else{
        $('#flow-tab-2').removeClass('active');
        $('#flow-tab-1').addClass('active');
        $('#flow-tabs-2').removeClass('show active');
        $('#flow-tabs-1').addClass('show active')

        $('#fa-row').show();
        $('#tr-row').show();
    }
})

$('#transfer-params').on('click',()=>{
    // Transfer parameters from signal simulation (left) to image acquisition (right)
    // Bright mode
    if ($('#contrast-type').val() === 'bright') {
        $('#thk').val($('#bright_thk').val()).change();
        $('#tr').val($('#bright_tr').val()).change();
        $('#fa').val($('#bright_fa').val()).change();
        $('#te').val($('#bright_te').val()).change();

    }
    // Dark mode
    else{
        $('#thk').val($('#dark_thk').val()).change();
        $('#te').val($('#dark_te').val()).change();
    }
})

$('#run-scan').on('click',()=>{
    socket.emit('Simulate flow image',{'thk': $('#thk').val(),
                                       'te': $('#te').val(),
                                       'fa': $('#fa').val(),
                                       'tr': $('#tr').val()});
})


socket.on('Deliver bright plots', (payload)=>{
    Plotly.newPlot('bright-chart-1',JSON.parse(payload['graph1']),{autosize:true});
    Plotly.newPlot('bright-chart-2',JSON.parse(payload['graph2']),{autosize:true});

})

socket.on('Deliver dark plots', (payload)=>{
    Plotly.newPlot('dark-chart-1',JSON.parse(payload['graph3']),{autosize:true});
    Plotly.newPlot('dark-chart-2',JSON.parse(payload['graph4']),{autosize:true});

})

socket.on('Deliver flow image',(payload)=>{
    Plotly.newPlot('image-chart',JSON.parse(payload['graph5']),{autosize:true});
})


// Syringe animation
let pushing = false;
window.onload = function(){
    let svgObj = document.getElementById('syringe');
    let svgDoc = svgObj.contentDocument;

    let svgItem = svgDoc.getElementById('animateSyringe');
    let svgItem2 = svgDoc.getElementById('animateReservoir');

    // Set animation speed based on current flow speed

    $('#flow-manual-button').on('click',()=> {
            let speed = parseFloat($("#flow_speed").val());
            if (speed > 0){
                let animationDuration = 2 / (speed / 20);
                svgItem.setAttribute('dur',`${animationDuration}s`)
                svgItem2.setAttribute('dur',`${animationDuration}s`)

                if (!pushing) {
                    console.log('Start pushing the syringe!!!');
                    svgItem.beginElement();
                    svgItem2.beginElement();

                    pushing = true;
                }
                else{
                    console.log('Stop pushing the syringe.');
                    svgItem.endElement();
                    svgItem2.endElement();

                    pushing = false;
                }
            }


    })
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
        socket.emit('game 4 question answered',{'ind': q_ind, 'correct': true});
    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-failure-text-${q_ind}`).removeClass('d-none');
        $(`#mc-success-text-${q_ind}`).addClass('d-none');
        // Hide success text
        socket.emit('game 4 question answered',{'ind': q_ind, 'correct': false});
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
            socket.emit('game4 update progress',{'task': task_id});
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

function go_to_next_tab(step) {
    if (step < 4) {
        $(`#task${step + 1}-tab`).removeClass('disabled');
        $(`#task${step + 1}-tab`).tab('show');
        $(`#step${step}`).removeClass('show active');
        $(`#step${step + 1}`).addClass('show active');
        // Change to default parameters for that task
    }
}

