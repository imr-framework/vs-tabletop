// Initialize socket
let socket = io();

$('#link-to-game6').addClass('text-success');

// Switch mode
$('#tab-t1').on('click',()=>{
    //
    console.log('Tab T1 clicked');
    socket.emit("Change to T1",{});
})

$('#tab-t2').on('click',()=>{
    // Send signal to backend to re-deliver all plots
    console.log('Tab T2 clicked');
    socket.emit("Change to T2",{});
})

$('.simulation-button').on('click',()=>{
    socket.emit('Change to simulation mode');
    $('#left-chart-header').text('Spin animation')
    $('#middle-chart-header').text('Magnetization');
    $('#right-chart-header').text('Pulse sequence');
})

$('.mapping-button').on('click',()=>{
    socket.emit("Change to mapping mode");
    $('#left-chart-header').text('Images')
    $('#middle-chart-header').text('ROI signal');
    $('#right-chart-header').text('Map');

})

$('.session-input').on('change',(event)=>{
    console.log('Session input changed...')
    socket.emit("Update parameter for Game 6", {'id': event.target.id, 'value': event.target.value});
})

socket.on('Update plots',(payload)=>{
    let u = 0;
    console.log(payload);
    for (let key in payload['plots']) {
        if (payload['disp'][key]) {
            Plotly.newPlot(`chart-${key}`, JSON.parse(payload['plots'][key]), {autosize: true});
        }}
})

$('#t1-scan').on('click',()=>{
    socket.emit("Scan T1",{'ti_array_text': $('#t1_map_TIs').val()});

})

$('#t2-scan').on('click',()=>{
    socket.emit("Scan T2",{'te_array_text':$('#t2_map_TEs').val()});
})

$('#t1-fit').on('click',()=>{
    for (let u = 1; u<=4; u++){
        if ($(`#t1_sphere${u}`).prop('checked')){
            n = u;
            break;
        }
    }
    socket.emit('Fit T1',{'sphere': n}); // Convey current selected sphere

})

$('#t2-fit').on('click',()=>{
    for (let u = 1; u<=4; u++){
        if ($(`#t2_sphere${u}`).prop('checked')){
            n = u;
            break;
        }
    }
    socket.emit('Fit T2',{'sphere':n});
})


$('.t1_sphere').on('click',(event)=>{
    let ind = event.target.id.slice(-1);
    console.log(ind);
    console.log(event.target.id);
    socket.emit('Find T1 ROI signal', {'sphere': ind});
})

$('.t2_sphere').on('click',(event)=>{
    console.log('T2 sphere #')
    let ind = event.target.id.slice(-1);
    console.log(ind);
    socket.emit('Find T2 ROI signal', {'sphere': ind});
})

socket.on('Add circle to image',(payload)=>{
    console.log(payload);
    c = payload['center'];
    r = payload['radius'];
    console.log(c[0]);
    console.log(r);
    update = {
        shapes:[
           {
            type: 'circle',
            xref: 'x',
            yref: 'y',
            x0: c[1]-r,
            y0: c[0]-r,
            x1: c[1]+r,
            y1: c[0]+r,
            opacity: 0.8,
            fillcolor: 'rgba(0,0,0,0)',
            line: {
                width: 5,
                color: 'limegreen'
            }
        }]
    }
    Plotly.relayout('chart-left',update);
})

$('#t1-map').on('click',()=>{
    socket.emit('Map T1', {});
    // Disable button temporarily while displaying spinning thingy
    $('#t1-map').attr('disabled',true);
    $('#t1-map-text').text("Calculating...");
    $('#t1-map-spinner').removeClass('d-none');
    // TODO for the tabs, make sure T1 MAP is on
    $('#t1-pht-disp').prop('checked',false);
    $('#t1-map-disp').prop('checked',true);


})

$('#t2-map').on('click',()=>{
    socket.emit('Map T2', {});
    $('#t2-map').attr('disabled',true);
    $('#t2-map-text').text("Calculating...");
    $('#t2-map-spinner').removeClass('d-none');
    // TODO for the tabs, make sure T2 MAP is on
    $('#t2-pht-disp').prop('checked',false);
    $('#t2-map-disp').prop('checked',true);


})


socket.on('Reset T1 map button',()=>{
    $('#t1-map').attr('disabled',false);
    $('#t1-map-text').text("Map");
    $('#t1-map-spinner').addClass('d-none');
})


socket.on('Reset T2 map button',()=>{
    $('#t2-map').attr('disabled',false);
    $('#t2-map-text').text("Map");
    $('#t2-map-spinner').addClass('d-none');
})

$('#t1-pht-disp').on('click',()=>{
    // Switch to phantom display
    socket.emit('T1 switch to phantom');
})

$('#t2-pht-disp').on('click',()=>{
    socket.emit('T2 switch to phantom');
})

$('#t1-map-disp').on('click',()=>{
    socket.emit('T1 switch to map');
})

$('#t2-map-disp').on('click',()=>{
    socket.emit('T2 switch to map');
})

$('#set-ti-array').on('click',()=>{
    // Get values of min, max, and number of TIs
    let min_ti = parseFloat($("#t1-min-ti").val());
    let max_ti = parseFloat($('#t1-max-ti').val());
    let num_ti = parseInt($('#t1-num-ti').val());
    let step = parseFloat((max_ti - min_ti) / (num_ti - 1));
    let ti_array_text = `${min_ti}`;
    // Calculate TI array
    for (let ti_ind = 1; ti_ind < num_ti; ti_ind++){
        ti_array_text += `,${Math.round(min_ti + ti_ind * step)}`;
    }
    // Send TI array text field to the correct values
    $('#t1_map_TIs').val(ti_array_text);
})

$('#set-te-array').on('click',()=>{
    console.log('Setting TE array?');
    let min_te = parseFloat($("#t2-min-te").val());
    let max_te = parseFloat($("#t2-max-te").val());
    let num_te = parseFloat($("#t2-num-te").val());
    let step = parseFloat((max_te - min_te) / (num_te - 1));
    let te_array_text = `${min_te}`;
    for (let te_ind = 1; te_ind < num_te; te_ind++){
        te_array_text += `,${Math.round(min_te + te_ind * step)}`;
    }
    $('#t2_map_TEs').val(te_array_text);
})




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
        socket.emit('game 6 question answered',{'ind': q_ind, 'correct': true});
    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-failure-text-${q_ind}`).removeClass('d-none');
        $(`#mc-success-text-${q_ind}`).addClass('d-none');
        // Hide success text
        socket.emit('game 6 question answered',{'ind': q_ind, 'correct': false});
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
            socket.emit('game6 update progress',{'task': task_id});
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



