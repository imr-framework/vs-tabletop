import Interactive from "https://vectorjs.org/interactive.js";



// Construct an interactive within the HTML element with the id "my-interactive"
let myInteractive = new Interactive("my-interactive-game2");


// Sizing
let total_width = $('#my-interactive-game2').parent().parent().innerWidth();
console.log('total_width');
console.log(total_width);
console.log('parent element');
console.log( $('#my-interactive-game2').parent());
const W = total_width*0.5;
const H = total_width*0.5;
const cc = [W/2, H/2];

myInteractive.width = W;
myInteractive.height = H;
myInteractive.originX = 0;
myInteractive.originY = 0;
myInteractive.border = true;

//Define static elements
// Square
let start = W/8;
let Wsq = W*0.75;
let square = myInteractive.rectangle(start,start,Wsq, Wsq);

square.style.fill = 'gray';
square.style.stroke = 'black';
square.style.strokeWidth='2px';

let gap = W/16;
let slice1 = Wsq*0.25;
let slice2 = Wsq*0.75;


// Make 4 primary controls and fix trajectory
let control_left = myInteractive.control(start + slice1, gap);
let control_right = myInteractive.control(start + slice2, gap);
let control_top = myInteractive.control(gap,start + slice1);
let control_bottom = myInteractive.control(gap,start + slice2);


// Calculation and highlight center
let selectSquare = myInteractive.rectangle(start+slice1,start+slice1,0.5*Wsq,0.5*Wsq);
selectSquare.style.fill = 'lightgray';
selectSquare.style.stroke = 'black';
selectSquare.style.strokeWidth = '1px';
selectSquare.addDependency(control_left,control_right,control_top,control_bottom);

selectSquare.update = function(){
    selectSquare.x = Math.min(control_left.x, control_right.x);
    selectSquare.y = Math.min(control_top.y, control_bottom.y)
    selectSquare.width = Math.abs(control_right.x - control_left.x);
    selectSquare.height = Math.abs(control_bottom.y - control_top.y);
}

// Central marking lines
let xaxis = myInteractive.line(start, W/2, W-start,W/2);
let yaxis = myInteractive.line(W/2, start, W/2, W-start);
xaxis.style.stroke = 'goldenrod';
xaxis.style.strokeWidth = '2px';
xaxis.style.strokeDasharray='6 6';

yaxis.style.stroke = 'goldenrod';
yaxis.style.strokeWidth = '2px';
yaxis.style.strokeDasharray='6 6';

// Make initial control lines & add dependency
// Left
let line_left = myInteractive.line(start+Wsq*0.25, gap, start+Wsq*0.25,W-gap);
line_left.addDependency(control_left);
line_left.update = function(){
    line_left.x1 = control_left.x;
    line_left.x2 = control_left.x;
}
// Right
let line_right = myInteractive.line(start+Wsq*0.75, gap, start+Wsq*0.75,W-gap);
line_right.addDependency(control_right);
line_right.update = function(){
    line_right.x1 = control_right.x;
    line_right.x2 = control_right.x;
}
// Top
let line_top = myInteractive.line(gap, start + slice1, W-gap, start + slice1);
line_top.addDependency(control_top);
line_top.update = function(){
    line_top.y1 = control_top.y;
    line_top.y2 = control_top.y;
}

// Bottom
let line_bottom = myInteractive.line(gap, start + slice2, W-gap, start + slice2);
line_bottom.addDependency(control_bottom);
line_bottom.update = function(){
    line_bottom.y1 = control_bottom.y;
    line_bottom.y2 = control_bottom.y;
}

// Dynamic constraints
control_left.root.setAttribute('id','control-left');
control_left.constrainWithinBox(start,gap,W-start,gap);
control_right.constrainWithinBox(start,gap,W-start,gap);
control_top.constrainWithinBox(gap,start,gap,W-start);
control_bottom.constrainWithinBox(gap,start,gap,W-start);



// Inversion
function invertSelection(){
    let fill2 = selectSquare.style.fill;
    selectSquare.style.fill = square.style.fill;
    square.style.fill = fill2;
}

function reset(){
    control_left.x = start + slice1;
    control_left.y = gap;
    control_right.x = start + slice2
    control_right.y = gap;
    control_top.x = gap;
    control_top.y = start + slice1;
    control_bottom.x = gap;
    control_bottom.y = start + slice2;
    selectSquare.style.fill = 'lightgray';
    square.style.fill = 'gray';
    line_left.update();
    line_right.update();
    line_top.update();
    line_bottom.update();
    selectSquare.update();

}


$('#invert-slicer').on('click',()=>{
    invertSelection();

})

$('#reset-slicer').on('click',()=>{
    reset();
})

$('#use-slicer').on('click',()=>{

})

// TODO
// Retrieve mask limits so we can generate a binary mask back in Python
export function getMaskValues(){
    let y1 = (Math.min(control_left.x,control_right.x) - start)/Wsq;
    let y2 = (Math.max(control_left.x,control_right.x) - start)/Wsq;
    let x1 = (Math.min(control_top.y,control_bottom.y) - start)/Wsq;
    let x2 = (Math.max(control_top.y,control_bottom.y) - start)/Wsq;
    let inverted = (selectSquare.style.fill==='gray');
    let info = {'x1':x1, 'x2':x2, 'y1':y1, 'y2':y2, 'inverted':inverted};
    return info;
}