// function fetchXML  (url, callback) {
//     var xhr = new XMLHttpRequest();
//     xhr.open('GET', url, true);
//     xhr.onreadystatechange = function (evt) {
//     //Do not explicitly handle errors, those should be
//     //visible via console output in the browser.
//     if (xhr.readyState === 4) {
//         callback(xhr.responseXML);
//     }
//     };
//     xhr.send(null);
// }
//
// //fetch the document
// fetchXML("static/img/mountain_vector.svg",function(newSVGDoc){
//     //import it into the current DOM
//     var n = document.importNode(newSVGDoc.documentElement,true);
//     document.documentElement.appendChild(n);
//     var circle = document.getElementById("circ-num-3");
//     console.log(circle);
// })
//

window.onload = function(){
    let svgObj = document.getElementById('the_mountain');
    let svgDoc = svgObj.contentDocument;


    for (let u = 1; u < 9; u++){
        let highlight;
        if (u % 2 === 0){
            console.log(u);
            highlight = 'bg-info';
        }
        else {
            highlight = 'bg-warning';
        }
        let svgItem = svgDoc.getElementById(`circ-num-${u}`);
        let myCirc = svgDoc.getElementById(`circ${u}`);
        $(svgItem).on('mouseover',()=>{
            console.log('in');
            $(`#game-card-${u}`).removeClass("bg-secondary").addClass(highlight);
        }).on('mouseout',()=>{
            console.log('out')
            $(`#game-card-${u}`).removeClass(highlight).addClass('bg-secondary');
    
        })

        $(`#game-card-${u}`).on('mouseover',()=>{
            svgItem.setAttribute('transform-origin',`${myCirc.getAttribute('cx')} ${myCirc.getAttribute('cy')}`);
            svgItem.setAttribute('transform','scale(1.2)');
        }).on('mouseout',()=>{
            svgItem.setAttribute('transform','');
        })

        }
    


}

for (let num=1;num<=8;num++) {
       let highlight;
        if (num % 2 === 0){
            highlight = 'bg-info';
        }
        else {
            highlight = 'bg-warning';
        }
    $(`#game-card-${num}`).hover(
        // "IN" function
        () => {
            console.log('in');
            $(`#game-card-${num}`).removeClass("bg-secondary").addClass(highlight);
        },
        // "OUT" function
        () =>{
            console.log('out')
            $(`#game-card-${num}`).removeClass(highlight).addClass('bg-secondary');
        }
    )


}
