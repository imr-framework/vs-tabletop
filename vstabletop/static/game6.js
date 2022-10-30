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
    socket.emit("Scan T1",{});
})

$('#t1-fit').on('click',()=>{
    for (let u = 1; u<=4; u++){
        console.log(u);
        if ($(`#t1_sphere${u}`).prop('checked')){
            n = u;
            break;
        }
    }
    socket.emit('Fit T1',{'sphere': n}); // Convey current selected sphere

})

$('.t1_sphere').on('click',(event)=>{
    let ind = event.target.id.slice(-1);
    console.log(ind);
    console.log(event.target.id);
    socket.emit('Find ROI signal', {'sphere': ind});
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
            x0: c[0]-r,
            y0: c[1]-r,
            x1: c[0]+r,
            y1: c[1]+r,
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
    socket.emit('Map T1', {})
    // Disable button temporarily while displaying spinning thingy
    $('#t1-map').attr('disabled',true);
    $('#t1-map-text').text("Calculating...");
    $('#t1-map-spinner').removeClass('d-none');

})

socket.on('Reset T1 map button',()=>{
    $('#t1-map').attr('disabled',false);
    $('#t1-map-text').text("Map");
    $('#t1-map-spinner').addClass('d-none');
})

$('#t1-pht-disp').on('click',()=>{
    // Switch to phantom display
    socket.emit('T1 switch to phantom');
})

$('#t1-map-disp').on('click',()=>{
    socket.emit('T1 switch to map');
})