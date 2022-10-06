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
        console.log(mode);
    }
    else{
        $('#flow-manual-button').text('PUSH').removeClass('btn-danger').addClass('btn-info');
        socket.emit('Flow off')
        // TODO stop animation frame

    }


})

$('#flow_speed').on('change',()=>{
    $('#flow-info').text(`Flow speed: ${20*$('#flow_speed').val()/100} mm / s`);
})

$(':input').on('change', (event)=>{
    socket.emit("Update parameter for Game 4", {'id': event.target.id, 'value': event.target.value});
})

$('#T1').on('change',()=>{
    $('#t1-display').text($('#T1').val())
})

$('#T2').on('change',()=>{
    $('#t2-display').text($('#T2').val())
})

$('#run-scan').on('click',()=>{
    // Signal backend to simulate an image!

})

$('#flow-tab-1').on('click',()=>{
    socket.emit('Toggle mode',{'mode':'bright'})
    // TODO change contrast type under image
    $('#contrast-type').val('bright');
})

$('#flow-tab-2').on('click',()=>{
    socket.emit('Toggle mode',{'mode':'dark'})
    // TODO change contrast type under image
    $('#contrast-type').val('dark');

})


socket.on('Deliver bright plots', (payload)=>{
    Plotly.newPlot('bright-chart-1',JSON.parse(payload['graph1']),{autosize:true});
    Plotly.newPlot('bright-chart-2',JSON.parse(payload['graph2']),{autosize:true});

})



socket.on('Deliver dark plots', (payload)=>{
    Plotly.newPlot('dark-chart-1',JSON.parse(payload['graph3']),{autosize:true});
    Plotly.newPlot('dark-chart-2',JSON.parse(payload['graph4']),{autosize:true});

})