let socket = io();

$(':input').on('change', (event)=>{
    socket.emit("Update param for Game7", {'id': event.target.id, 'value': event.target.value});
})

socket.on('G7 take session data', msg=>{
    $('#proj3d').val(msg['data']['proj3d']);
    $('#proj2d').val(msg['data']['proj2d']);
    console.log(msg['data'])
})