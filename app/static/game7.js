let socket = io();
let layout = {autosize: true};

$(':input').on('change', (event)=>{
    socket.emit("Update param for Game7", {'id': event.target.id, 'value': event.target.value});
})



$('#button-3d-model').on('click',()=>{
    socket.emit("Request 3D model")
})

$('#button-2d-proj').on('click',()=>{
    socket.emit("Request 2D projection")
})

$('#button-1d-proj').on('click',()=>{
    socket.emit("Request 1D projection")
})

$('#lines-toggle').on('click',()=>{
    socket.emit("Toggle line display")
})

socket.on('Deliver 3D model', (payload)=>{
    graphData1 = JSON.parse(payload['graph1'])
    graphData2 = JSON.parse(payload['graph2'])
    graphData3 = JSON.parse(payload['graph3'])
    Plotly.newPlot('chart-G7-3D',graphData1,layout)
    Plotly.newPlot('chart-G7-2D',graphData2,layout)
    Plotly.newPlot('chart-G7-1D',graphData3,layout)
})

socket.on('Deliver 2D projection', (payload)=>{
    graphData = JSON.parse(payload['graph']);
    Plotly.newPlot('chart-G7-2D',graphData,layout)
})

socket.on('Deliver 1D projection', (payload)=>{
    graphData = JSON.parse(payload['graph']);
    Plotly.newPlot('chart-G7-1D',graphData,layout)

})