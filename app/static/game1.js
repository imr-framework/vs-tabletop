let socket = io();

$(':input').on('input', (event)=>{
    socket.emit("Update param for Game1", {'id': event.target.id, 'value': event.target.value});
})