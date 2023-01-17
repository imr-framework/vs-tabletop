const layout = {autosize: true};
let graphData;
$('#link-to-game2').addClass('text-success');
let socket = io();


// TODO add in instantaneous variables! Don't use session ones ...
$('#fetch-signal').on('click',()=>{
    let name = $('#signal_name_field').val();
    socket.emit('Request signal',{'name':name,
                                  'signal_scale': parseFloat($('#signal_scale').val()),
                                    'signal_stretch': parseFloat($('#signal_stretch').val()),
                                   'signal_shift': parseFloat($('#signal_shift').val()),

                                   'signal_phase_mod': parseFloat($('#signal_phase_mod').val())});
})

$('#fetch-image').on('click',()=>{
    let name = $('#image_name_field').val();
    socket.emit('Request image', {'name':name,
                                   'image_angle': parseFloat($('#image_angle').val()),
                                   'image_wavelength': parseFloat($('#image_wavelength').val()),
                                   'image_wave_phase': parseFloat($('#image_wave_phase').val())});
})

$('#fetch-kspace').on('click',()=>{
    let name = $('#kspace_name_field').val();
    socket.emit('Request kspace', {'name':name,
                                   'kspace_angle': parseFloat($('#kspace_angle').val()),
                                    'kspace_ds_separation': parseFloat($('#kspace_ds_separation').val())});
})

$('#fetch-spectrum').on('click',()=>{
    let name = $('#spectrum_name_field').val();
    socket.emit('Request spectrum', {'name':name,
                                     'spectrum_scale': parseFloat($('#spectrum_scale').val()),
                                    'spectrum_stretch': parseFloat($('#spectrum_stretch').val()),
                                    'spectrum_shift': parseFloat($('#spectrum_shift').val()),
                                    'spectrum_phase_mod': parseFloat($('#spectrum_phase_mod').val())});
})


socket.on('Deliver signal', (payload)=>{
    graphData = JSON.parse(payload['graph'])
    Plotly.newPlot('chart-left',graphData,layout)

})

socket.on('Deliver image', (payload)=>{
    graphData = JSON.parse(payload['graph'])
    Plotly.newPlot('chart-left',graphData,layout)

})


socket.on('Deliver spectrum', (payload)=>{
    graphData = JSON.parse(payload['graph'])
    Plotly.newPlot('chart-right',graphData,layout)

})


socket.on('Deliver kspace', (payload)=>{
    graphData = JSON.parse(payload['graph'])
    Plotly.newPlot('chart-right',graphData,layout)

})

// Transforms
$('#forward-transform').on('click',()=>{
    socket.emit('Perform forward transform')
})

$('#backward-transform').on('click',()=>{
    socket.emit('Perform backward transform')
})

// Fabric canvas
// Canvas 1 : drawing
let canvas = new fabric.Canvas('drawing',{
    isDrawingMode: true
});
canvas.setHeight(400);
canvas.setWidth(400);
canvas.setBackgroundColor('white');
canvas.renderAll();


$('#clear-drawing').on('click',()=>{
    canvas.clear();
    canvas.setBackgroundColor('white');
    canvas.renderAll();
})

$('#fill-drawing').on('click',()=>{
    canvas.clear();
    canvas.setBackgroundColor('black');
    canvas.renderAll();
})

$('#drawing-width').on('change',()=> {
    console.log('Width changed');
    canvas.freeDrawingBrush.width = parseInt($('#drawing-width').val(), 10) || 1;
    $('#drawing-width-info').text(parseInt($('#drawing-width').val(), 10) || 1);
    console.log(canvas.freeDrawingBrush.width);
  });

$('#drawing-graylevel').on('change',()=> {
    console.log('Color changed');
    let gl = (255/100)*(parseInt($('#drawing-graylevel').val(), 10) || 1);
    canvas.freeDrawingBrush.color = `rgb(${gl},${gl},${gl})`;
    $('#drawing-graylevel-info').text(parseInt($('#drawing-graylevel').val(), 10) || 1);
  });


$('#use-drawing').on('click',()=>{
    let drawing = canvas.toDataURL({format:'png'});
    socket.emit('Send drawing',{'url':drawing});

})

// Canvas 2: erase

let canvas2 = new fabric.Canvas('erase',{
    isDrawingMode: true
});
canvas2.setHeight(400);
canvas2.setWidth(400);
canvas2.setBackgroundColor('lightgreen');
canvas2.renderAll();

canvas2.freeDrawingBrush.color = 'black';
canvas2.freeDrawingBrush.width = 50;



$('#erase-width').on('change',()=> {
    canvas2.freeDrawingBrush.width = parseInt($('#erase-width').val(), 10) || 10;
    $('#erase-width-info').text(parseInt($('#erase-width').val(), 10) || 10);
  });

$('#erase-reset').on('click',()=>{
    canvas2.clear();
    canvas2.setBackgroundColor('lightgreen');
    canvas2.renderAll();
    socket.emit('Reset erase');
})

$('#erase-apply').on('click',()=>{
    let erase = canvas2.toDataURL({format:'png'});
    socket.emit('Send erase',{'url': erase});
})

// Slicer communications
import {getMaskValues} from "./slicer.js";

function getUndersamplingInfo(){
    // Retrieve undersampling factors
    return {
        'usf-x': $('#undersample_x_field').val(),
        'usf-y': $('#undersample_y_field').val()
    }
}

$('#use-slicer').on('click',()=>{
    // Mask
    let slicerInfo = Object.assign(getMaskValues(), getUndersamplingInfo())
    console.log(slicerInfo);
    socket.emit('Use slicer info', slicerInfo);
})

$('#upload-button').on('click',()=>{
    let formData = new FormData($('#upload-form').get(0));

    $.ajax({
        type: 'POST',
        url : '/games/2',
        data: formData,
        success:function(data){
        },
        cache: false,
        contentType: false,
        processData: false
    })
})

$('#recover-button').on('click',()=>{
    socket.emit('Request image','upload');
})

// Others
$('.preset-input').on('change',(event)=>{
    console.log('Preset input changed');

    // Request session to go back to source=preset
    socket.emit('Go back to preset');

    // Update session parameter
    socket.emit('Update parameter for Game 2', {'id': event.target.id, 'value': event.target.value});

})

// Messaging

socket.on('message', (msg)=>{
    let added_class;
    if (msg['type']==='warning'){
        added_class = 'text-danger';
    }
    else if (msg['type']==='success'){
        added_class = 'text-success';
    }
    else{
        added_class = 'text-primary';
    }
    $('#message-region').text(msg['text']).removeClass('text-success text-danger text-primary').addClass(added_class);
    $('#megaphone').removeClass('text-success text-danger text-primary').addClass(added_class)
})

// Instructions
// Task completion tracking
$(".task-next-button").click((event)=>{
    let task_id = event.target.id.replace('task','').replace('-next','');
    // Check if all checkboxes of task are selected
    if ($(`input.task-${task_id}-check`).not(':checked').length === 0){
        console.log('All boxes are checked! Moving on.')
        // Update session progress
        socket.emit('game2 update progress',{'task': task_id});
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
        $(`#task${step+1}-tab`).removeClass('disabled').tab('show');
        $(`#step${step}`).removeClass('show active');
        $(`#step${step+1}`).addClass('show active');
    }
}

// Multiple choice
let submit_id;
let q_ind;
let choice;
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
        socket.emit('game 2 question answered',{'ind':q_ind, 'correct':true});

    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-success-text-${q_ind}`).addClass('d-none')
        $(`#mc-failure-text-${q_ind}`).removeClass('d-none')
        socket.emit('game 2 question answered',{'ind':q_ind,'correct':false});

        // Hide success text
    }
    console.log('Updating choice')
})

// Star update
let num_stars, num_full, num_half, num_empty;
socket.on('renew stars',(msg)=>{
    console.log('Stars should be updated now...')
    num_stars = msg['stars'];
    num_full = parseInt(Math.floor(num_stars));
    num_half = parseInt(Math.round((num_stars-num_full)*2));
    num_empty = 5 - num_full - num_half;


    let stars_html = ""
    stars_html += '<i class="bi bi-star-fill text-warning"></i> '.repeat(num_full)
    stars_html += '<i class="bi bi-star-half text-warning"></i> '.repeat(num_half)
    stars_html += '<i class="bi bi-star text-warning"></i> '.repeat(num_empty)

    $("#stars-display").html(stars_html);

})

// Collapse all steps when tab is opened up
$('.taskstep').removeClass('show');
