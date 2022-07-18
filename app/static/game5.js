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


// Button functions
$('#start').on('click',()=>{
    socket.emit('simulate precession')
})

$('#tip').on('click',()=>{
    socket.emit('simulate nutation')
})

$('#reset').on('click',()=>{
    socket.emit('reset everything')
})

function play_animation(graphData){
    let mx, my, mz;
    let time_ind = 0;
    let data_length = graphData.data[0].x.length;

    // TODO have index keep track of animation ... animate only until last point; then keep it fixed
    Plotly.newPlot('chart-spin', {
        // Data
        data: [{
                type: 'scatter3d',
                x: [0, graphData.data[0].x[0]],
                y: [0, graphData.data[0].y[0]],
                z: [0, graphData.data[0].z[0]],
                mode: 'lines',
                line: graphData.data[0].line
        },
            graphData.data[1], graphData.data[2], graphData.data[3]
            ],
        layout: graphData.layout
    });


    // Retrieve next frame
    function compute(ind){
        mx = graphData.data[0].x[ind];
        my = graphData.data[0].y[ind];
        mz = graphData.data[0].z[ind];
    }

    // Animate plot with all succeeding points
    function update(){
            compute(time_ind);
            Plotly.animate('chart-spin', {
                // A. Plot
                // B. Data
            data: [{
                type: 'scatter3d',
                    x: [0,mx],
                    y: [0,my],
                    z: [0,mz],
                    mode: 'lines',
                    line: graphData.data[0].line}],
                // Layout
            layout: graphData.layout},
                // B. Animation options
           {
            transition: {
              duration: 0
            },
            frame: {
              duration: 10,
              redraw: true
            }
          });
        // Stop increasing it once it hits the end
        if (time_ind < data_length - 1){
            time_ind ++;
        }
        requestAnimationFrame(update)
        }
        requestAnimationFrame(update);

}