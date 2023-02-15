let socket = io();

$('#run-scan').on('click',()=>{
    console.log('Run experiment!');
    // Send info to socket to start the experiment using uploaded seq file

})


$('#upload-button').on('click',()=>{
    let formData = new FormData($('#upload-form').get(0));

    $.ajax({
        type: 'POST',
        url : '/scan',
        data: formData,
        success:function(data){
        },
        cache: false,
        contentType: false,
        processData: false
    })


})

socket.on("Seq file uploaded",()=>{
    $("#display-seq").prop('disabled',false);
})

$("#display-seq").on("click",()=>{
    let minTime = $('#min_time_field').val();
    let maxTime = $('#max_time_field').val();
    socket.emit("Display sequence",{'min': minTime, 'max': maxTime});
})

socket.on("Deliver seq plot",(payload)=>{
    Plotly.newPlot('psd-chart',JSON.parse(payload['graph']), {autosize: true});
})

$("#compile-seq").on("click",()=>{
    socket.emit("Compile sequence",{'mode':$("#scan-mode").val()});

})

socket.on("Message",(payload)=>{
    $("#message-region").text(payload['text']);
    $("#message-region").addClass(`text-${payload['type']}`);
})

$("#update-ip").on("click",()=>{
    let ip = $("#ip-address").val();
    console.log(ip);
    socket.emit("Update local config with ip",{'ip-address':ip});


})

$("#update-settings").on('click',()=>{
    socket.emit("Update config",{'f0':$("#f0").val(),
                                  'width':$("#pulse-width").val(),
                                  'power':$('#pulse-power').val()})
})

socket.on("Deliver Rx data",(payload)=>{
        Plotly.newPlot('rx-plot',JSON.parse(payload['graph']), {autosize: true});
})