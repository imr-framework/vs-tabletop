import Interactive from "https://vectorjs.org/interactive.js";


const W = 400;
const H = 400;


const cc = [W/2, H/2];
const R = H/3;
// Construct an interactive within the HTML element with the id "my-interactive"
let myInteractive = new Interactive("my-interactive");
myInteractive.width = W;
myInteractive.height = H;
myInteractive.originX = 0;
myInteractive.originY = 0;

myInteractive.border = true;

//Define static elements
// Text

//Big circle
let circle = myInteractive.circle(cc[0],cc[1], R);
let biggerCircle = myInteractive.circle(cc[0],cc[1],R*5/4);
//Center
let center = myInteractive.circle(cc[0],cc[1],3);
biggerCircle.style.fill='transparent';
biggerCircle.stroek = ' transparent';
circle.style.fill = 'transparent';
circle.style.stroke = 'Gray';
circle.style.strokeWidth = '3px';
center.style.fill = 'black';
center.style.stroke = 'Gray';
center.style.strokeWidth = '0px';
let lines = [];
// Wheel rungs x 8
for (let i = 0; i < 8; i++){
    let c = calculate_line_coordinates(cc,R,i*45);
    let line = myInteractive.line(c[0], c[1], c[2], c[3]);
    line.style.strokeWidth='2px';
    line.style.stroke= 'Gray';

    lines.push(line);
}
//line.style.stroke = 'red';


// Interactive elements
// Construct a control point at the the location (500, 50)
let control = myInteractive.control(cc[0],cc[1]/2-R/4);
control.root.setAttribute('id','eye-control-handle');
control.constrainTo(circle);
// Construct projection line
let projLine = myInteractive.line(cc[0]/2,R/4,cc[0]/2,cc[1]-R/4);
projLine.style.strokeWidth='2px';
projLine.style.stroke='DodgerBlue';


projLine.update = function () {
    this.x1 = control.x;
    this.y1 = control.y;
    this.x2 = cc[0] - (this.x1 - cc[0]);
    this.y2 = cc[1] - (this.y1 - cc[1]);

};
projLine.update();
projLine.addDependency(control);

// Display angle
let thetaDisplay = myInteractive.text(50, 30, `θ = 90 degrees`);
thetaDisplay.addDependency(control);
thetaDisplay.update = function () {
    thetaDisplay.contents = `θ = ${rad2Deg(getAngle()).toFixed(2)} degrees`;
    // thetaDisplay.contents = `θ = ${getAngle().toFixed(2)} or ${(getAngle()/(2*Math.PI)).toFixed(2)}τ`;
};
thetaDisplay.update();

// Loading eye.svg
import { getScriptName } from 'https://vectorjs.org/index.js';
import { getURL } from 'https://vectorjs.org/util/file.js';
import { parseSVG } from 'https://vectorjs.org/util/svg.js';

const svgSize = 32;
const x0 = cc[0] - svgSize / 2;
const y0 = cc[1] - R - 1.25 * svgSize;

class Eye {
  constructor(angle,color) {
      this.angle = angle;

      let group = myInteractive.group();
      let eye1 = myInteractive.path("M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z");
      let eye2 = myInteractive.path("M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z");
      group.root.appendChild(eye1.root);
      group.root.appendChild(eye2.root);
      group.style.fill = color;

      group.root.setAttribute('transform', `rotate(${this.angle},${cc[0]},${cc[1]}) translate(${x0},${y0}) scale(2)`);

      this.group = group;
  }
}
for (let q = 0; q < 8; q++) {
    const eye = new Eye(q*45, 'Gray');
}

const blueEye = new Eye(0,'DodgerBlue');
blueEye.group.root.setAttribute('id','blueEye');
blueEye.group.update = function(){
    this.root.setAttribute('transform',`rotate(${-rad2Deg(getAngle())+90},${cc[0]},${cc[1]}) translate(${x0},${y0}) scale(2)`);
    $('#proj1d_angle').val(rad2Deg(getAngle()));
    $('#proj1d_angle').trigger('change');
}
blueEye.group.update();
blueEye.group.addDependency(control)




//Helper functions
function calculate_line_coordinates(center,radius,angle){
    let x1 = radius * Math.cos(deg2Rad(angle));
    let y1 = radius * Math.sin(deg2Rad(angle));
    let x2 = -x1;
    let y2 = -y1;

    x1 += center[0];
    x2 += center[0];
    y1 += center[1];
    y2 += center[1];

    return [x1,y1,x2,y2];
}

function calculate_eye_coordinates(svgSize, angle){
    let x0 = cc[0] - svgSize/2;
    let y0 = cc[1] - R - 1.25*svgSize;

    let theta = deg2Rad(angle);
    let x = cc[0] + Math.cos(theta)*(x0-cc[0]) - Math.sin(theta)*(y0-cc[1]);
    let y = cc[1] + Math.sin(theta)*(x0-cc[0]) + Math.cos(theta)*(y0-cc[1]);

    return [x,y]
}


function getAngle(){
    let rx = control.x - cc[0];
    let ry = control.y - cc[1];
    if (ry <= 0) {
        return Math.abs(Math.atan2(ry, rx));
    }
    else {
        return Math.PI * 2 - Math.atan2(ry,rx);
    }
}


function deg2Rad(degrees) {
  return degrees * (Math.PI / 180);
}

function rad2Deg(rad) {
  return rad / (Math.PI / 180);
}