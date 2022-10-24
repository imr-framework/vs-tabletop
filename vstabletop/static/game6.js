// Initialize socket
let socket = io();

$('#link-to-game6').addClass('text-success');

// Switch mode

$('#tab-t1').on('click',()=>{
    //
    console.log('Tab T1 clicked');
    socket.emit("Change to T1",{});


})

$('#tab-t2').on('click',()=>{
    // Send signal to backend to re-deliver all plots
    console.log('Tab T2 clicked');
    socket.emit("Change to T2",{});
})


socket.on('Update plots',(payload)=>{
    for (let key in payload) {
     console.log(key, `chart-${key}`);
     Plotly.newPlot(`chart-${key}`,JSON.parse(payload[key]),{autosize:true});
    }
})