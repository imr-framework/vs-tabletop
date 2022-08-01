let socket = io();

$(':input').on('change', (event)=>{
    socket.emit("Update param for Game3", {'id': event.target.id, 'value': event.target.value});
    console.log('in input')
})

socket.on('G3 take session data', (msg)=>{
    console.log('Updating g3 data')
    $('#options').val(msg['data']['options']);
    $('#TR').val(msg['data']['TR']);
    $('#TE').val(msg['data']['TE']);
    $('#FA').val(msg['data']['FA']);
    console.log(msg['data'])
})

$('.carousel').carousel({
  interval: false,
});