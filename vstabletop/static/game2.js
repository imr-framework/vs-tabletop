const layout = {autosize: true};

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

$('#drawing-width').on('change',()=> {
    console.log('Width changed');
    canvas.freeDrawingBrush.width = parseInt($('#drawing-width').val(), 10) || 1;
    console.log(canvas.freeDrawingBrush.width);
  });

$('#use-drawing-2d').on('click',()=>{
//     fabric.log('cropped png dataURL: ', canvas.toDataURL({
//     format: 'png'
// }));
    let drawing2d = canvas.toDataURL({format: 'png'});
    socket.emit('Send 2D drawing',{'url':drawing2d});
})

$('#use-drawing-1d').on('click',()=>{
//     fabric.log('cropped png dataURL: ', canvas.toDataURL({
//     format: 'png'
// }));
    let drawing1d = canvas.toDataURL({format: 'png'});
    socket.emit('Send 1D drawing',{'url':drawing1d});
})