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
    console.log("Let's get the button displayed");
    $("#display-seq").removeClass('d-none');
})

$("#display-seq").on("click",()=>{
    socket.emit("Display sequence")
})

socket.on("Deliver seq plot",(payload)=>{
    Plotly.newPlot('psd-chart',JSON.parse(payload['graph']), {autosize: true})
})