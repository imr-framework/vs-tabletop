let socket = io();

$(':input').on('input', (event)=>{
    socket.emit("Update param for Game5", {'id': event.target.id, 'value': event.target.value,
                                           'checked':event.target.checked});
})

$('#mag-x').on('click',()=>{
    // theta = 90, phi = 0, |M| = 1
    $('#m_theta').val(90);
    $('#m_phi').val(0);
    $('#m_size').val(1.0);
})


$('#mag-y').on('click',()=>{
    // theta = 90, phi = 0, |M| = 1
    $('#m_theta').val(90);
    $('#m_phi').val(90);
    $('#m_size').val(1.0);
})


$('#mag-z').on('click',()=>{
    // theta = 90, phi = 0, |M| = 1
    $('#m_theta').val(0);
    $('#m_phi').val(0);
    $('#m_size').val(1.0);
})

$('#mag-0').on('click',()=>{
    $('#m_theta').val(0);
    $('#m_phi').val(0);
    $('#m_size').val(0);
})

$('#set-mag').on('click',()=>{
    socket.emit('reset magnetization');
})



// Plotting functions

