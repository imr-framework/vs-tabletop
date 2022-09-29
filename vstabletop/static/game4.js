// Initialize socket
let socket = io();

$('#link-to-game4').addClass('text-success');

$('#flow-manual-button').on("click",()=>{
    // Change status
    if ($('#flow-manual-button').text() === 'PUSH'){
        $('#flow-manual-button').text('STOP').removeClass('btn-info').addClass('btn-danger');
        socket.emit('Flow on')
    }
    else{
        $('#flow-manual-button').text('PUSH').removeClass('btn-danger').addClass('btn-info');
        socket.emit('Flow off')

    }


})

$('#flow-speed').on('change',()=>{
    $('#flow-info').text(`Flow speed: ${20*$('#flow-speed').val()/100} mm / s`);
})

$(':input').on('change', (event)=>{
    socket.emit("Update parameter for Game 4", {'id': event.target.id, 'value': event.target.value});
})
