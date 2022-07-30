let socket = io();

$(':input').on('change', (event)=>{
    socket.emit("Update param for Game1", {'id': event.target.id, 'value': event.target.value});
})

socket.on('G1 take session data', (msg)=>{
    console.log('I am supposed to be updating data')
    $('#Matrix_scale').val(msg['data']['Matrix_scale']);
    $('#Voxel_scale').val(msg['data']['Voxel_scale']);
    $('#FOV_scale').val(msg['data']['FOV_scale']);
    $('#zero_scale').val(msg['data']['zero_scale']);
    $('#P1_q').val(msg['data']['P1_q'])
    $('#P2_q').val(msg['data']['P2_q'])
    console.log(msg['data'])
})

$(document).ready(function(){
  $('.my-js-slider').wRunner({
       type: 'range',
       rangeValue: {
            minValue: 30,
            maxValue: 100,
                 },
       step: 1,
    })
})

