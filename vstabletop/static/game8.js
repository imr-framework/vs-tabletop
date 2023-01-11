let socket = io();


$('#link-to-game8').addClass('text-success');

$('#mode-2d').on('click',()=>{
    $('#mystery-image-3d').addClass('d-none');
    $('#prescription-3d').addClass('d-none');
    $('#3d-images-card').addClass('d-none');

    $("#mystery-image-2d").removeClass('d-none');
    $('#prescription-2d').removeClass('d-none');
    $('#2d-images-card').removeClass('d-none');

    socket.emit('Draw new 2D image');
})

$('#mode-3d').on('click',()=>{
    $("#mystery-image-3d").removeClass('d-none');
    $('#prescription-3d').removeClass('d-none');
    $('#3d-images-card').removeClass('d-none');

    $('#mystery-image-2d').addClass('d-none');
    $('#prescription-2d').addClass('d-none');
    $('#2d-images-card').addClass('d-none');
    socket.emit('Draw new 3D model');
})

$('#image-1d').on('click',()=>{
    socket.emit("Get 1D projection",{'angle':$('#proj1d_angle').val()});
})

$('#image-2d').on('click',()=>{
    let axis;
    $('.proj-2d-xyz').each(function(){
        console.log($(this)[0].checked);
        if ($(this)[0].checked){
            axis = $(this).val();
        }
    })
    socket.emit("Get 2D projection",{'axis': axis});

})

socket.on("Deliver options plot", (payload)=>{
    Plotly.newPlot('game8-choices-chart',JSON.parse(payload['graph']), {autosize: true});
})

socket.on("Message",(message)=>{
    $("#message-region").text(message['text']);
})


$(':input').on('change', (event)=>{
    socket.emit("Update parameter for game 8", {'id': event.target.id, 'value': event.target.value});
})

//'Deliver attempt plot', {'mode': '3D', 'graph': j1, 'attempt': num_attempts_sofar + 1
socket.on("Deliver attempt plot",(payload)=>{
    switch_to_tab(payload);
    setTimeout(() => {
         if (payload['mode'] === '3D'){
        Plotly.newPlot(`chart-3d-attempt${payload['attempt']}`, JSON.parse(payload['graph']), {autosize: true});
        console.log(`Attempt #${payload['attempt']}`);

        }
        else if (payload['mode'] === '2D'){
            Plotly.newPlot(`chart-2d-attempt${payload['attempt']}`, JSON.parse(payload['graph']), {autosize: true});

        }
    }, 500);


})

$('#reset-button').on('click',()=>{
    socket.emit("Reset attempts without changing question");
})

socket.on('Wipe all attempt plots',()=>{
    $('.chart-attempt').each(function(){
        Plotly.purge($(this).attr('id'));
    })
    $("#feedback-correct").addClass('d-none');
    $("#feedback-wrong").addClass('d-none');
    //$("#submit-button").attr('disabled',false);
    $('.submit-option').attr('disabled',false).prop('checked',false);
})

$("#new-model-button").on('click',()=>{
    console.log("New model requested");
    if ($('#2d-images-card').hasClass("d-none")){
        socket.emit('Draw new 3D model');
    }
    else{
        socket.emit("Draw new 2D image");
    }
})

$('.submit-option').on('click',()=>{
    $('#submit-button').attr('disabled',false);
})

$('#submit-button').on('click',()=>{
    // Which answer was chosen?
    let choice;
    $('.submit-option').each(function(){
        console.log($(this)[0].checked);
        if ($(this)[0].checked){
            choice = $(this).val();
        }
        $(this).attr('disabled',true);
    })
    socket.emit("Answer submitted",{'choice':choice})
    // Disable submit button
    $('#submit-button').attr('disabled',true);

})

socket.on("Correct",()=>{
    $("#feedback-correct").removeClass('d-none');
    $("#feedback-wrong").addClass('d-none');
})

socket.on("Wrong",()=>{
    $("#feedback-correct").addClass('d-none');
    $("#feedback-wrong").removeClass('d-none');
})

function switch_to_tab(payload){
    const someTabTriggerEl = document.querySelector(`#game8-${payload['mode'].toLowerCase()}-tab-${payload['attempt']-1}`);
    const tab = new mdb.Tab(someTabTriggerEl);
    tab.show();
}