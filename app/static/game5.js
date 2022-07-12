let socket = io();

$(':input').on('input', (event)=>{
    socket.emit("Update param for Game5", {'id': event.target.id, 'value': event.target.value});
})

