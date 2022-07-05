
let socket = io();
// When server emits an event of 'take this', display its message
socket.on('take this', (msg)=>{
    ///$('#declarer').text(msg.data);
});


socket.on('plots served', (msg)=>{
    //$('#declarer').text('FID & Spectrum plots should be served now...');
    // TODO use extend Traces so that the plot is UPDATED rather than REDRAWN - the goal is to stay zoomed in
    Plotly.newPlot('chart-left',JSON.parse(msg['fid']),{});
    Plotly.newPlot('chart-center',JSON.parse(msg['spectrum']),{});

} )

socket.on('fa plot served', (msg)=>{
    //$('#declarer').text('FA plot should be served now ... ');
    Plotly.newPlot('chart-right',JSON.parse(msg['fa_signal']),{});
})

$('#run-scan').click(()=> {
    // Emit signal to run scans while including current parameters
    let payload = {'f0':parseFloat($('#f0').val())*1e6,
        'shimx':parseFloat($('#shimx').val()),'shimy': parseFloat($('#shimy').val()),
        'shimz':parseFloat($('#shimz').val()),'tx_amp':parseFloat($('#tx-amp').val())};
    socket.emit('run scans',payload);
})

$('#stop-scan').click(()=>{
    socket.emit('stop scans',{'data':'Attempting to stop the scanning.'})
    }
)

$('#run-fa').click(()=>{
    socket.emit('run FA',{'data':'Start flip angle calibration.'})
})

$('#zero-shims').click(()=>{
    // Set shim values to zero
    $('#shimx').val(0.0)
    $('#shimy').val(0.0)
    $('#shimz').val(0.0)
    $('#shimx_val').val(0.0)
    $('#shimy_val').val(0.0)
    $('#shimz_val').val(0.0)

    // Send message to server to reset session shim values
    socket.emit('zero shims',{'data': 'Zeroing shim parameters!'})
})

// When any single parameter is changed, emit signal to server to update it
$(':input').on('input',(event)=>{
    socket.emit("update single param",{'id': event.target.id, 'value': event.target.value});
})