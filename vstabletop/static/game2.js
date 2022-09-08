const layout = {autosize: true};
let graphData;
$('#link-to-game2').addClass('text-success');
let socket = io();


$('#fetch-signal').on('click',()=>{
    let name = $('#signal_name_field').val();
    socket.emit('Request signal',{'name':name});
})

$('#fetch-image').on('click',()=>{
    let name = $('#image_name_field').val();
    socket.emit('Request image', {'name':name});
})

$('#fetch-kspace').on('click',()=>{
    let name = $('#kspace_name_field').val();
    socket.emit('Request kspace', {'name':name});
})

$('#fetch-spectrum').on('click',()=>{
    let name = $('#spectrum_name_field').val();
    socket.emit('Request spectrum', {'name':name});
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

// TODO Image upload - prevents page from reloading
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