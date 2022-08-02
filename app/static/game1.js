let tabs = document.querySelectorAll('.tabs__toggle'),
    contents = document.querySelectorAll('.tabs__content');

tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
        contents.forEach((content) => {
            content.classList.remove('is-active');
        });
        tabs.forEach((tab) => {
            tab.classList.remove('is-active');
        });
        contents[index].classList.add('is-active');
        tabs[index].classList.add('is-active');
    });
});
let socket = io();

$(':input').on('change', (event)=>{
    console.log('Updating')
    socket.emit("Update param for Game1", {'id': event.target.id, 'value': event.target.value});
})

$('.answer-mc').on('click', (event)=>{
    submit_id = event.target.id;
    q_ind = submit_id[submit_id.length-1]
    console.log(submit_id);
    choice = $(`.q${q_ind}-choice:checked`).attr("value");

    console.log(choice)

    let letters = ['a','b','c','d'];

    if (choice == letters[parseInt($(`#mc-correct-choice-${q_ind}`).text())]){
        console.log("Answer is correct! ")
        // Make success text visible
        $(`#mc-success-text-${q_ind}`).removeClass('d-none')
    }
    else{
        console.log("Answer is wrong! ")
        $(`#mc-success-text-${q_ind}`).addClass('d-none')
        // Hide success text
    }


    //choice="some choice"
    console.log('Updating choice')
    //socket.emit("Updating choice for Game 1", {'choice':choice});
})

socket.on('G1 take session data', (msg)=>{
    console.log('I am supposed to be updating data')
    $('#Matrix_scale').val(msg['data']['Matrix_scale']);
    $('#Voxel_scale').val(msg['data']['Voxel_scale']*1000);
    $('#FOV_scale').val(msg['data']['FOV_scale']*1000);
    $('#zero_fill').val(msg['data']['zero_fill']);
    $('#Min_scale').val(msg['data']['Min_scale']);
    $('#Max_scale').val(msg['data']['Max_scale']);
    $('#P1_q').val(msg['data']['P1_q'])
    $('#P2_q').val(msg['data']['P2_q'])
    console.log(msg['data'])
})
// a comment

function controlFromInput(fromSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#25daa5', controlSlider);
    if (from > to) {
        fromSlider.value = to;
        fromInput.value = to;
    } else {
        fromSlider.value = from;
    }
}

function controlToInput(toSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#25daa5', controlSlider);
    setToggleAccessible(toInput);
    if (from <= to) {
        toSlider.value = to;
        toInput.value = to;
    } else {
        toInput.value = from;
    }
}

function controlFromSlider(fromSlider, toSlider, fromInput) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
  if (from > to) {
    fromSlider.value = to;
    fromInput.value = to;
  } else {
    fromInput.value = from;
  }
}

function controlToSlider(fromSlider, toSlider, toInput) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
  setToggleAccessible(toSlider);
  if (from <= to) {
    toSlider.value = to;
    toInput.value = to;
  } else {
    toInput.value = from;
    toSlider.value = from;
  }
}

function getParsed(currentFrom, currentTo) {
  const from = parseInt(currentFrom.value, 10);
  const to = parseInt(currentTo.value, 10);
  return [from, to];
}

function fillSlider(from, to, sliderColor, rangeColor, controlSlider) {
    const rangeDistance = to.max-to.min;
    const fromPosition = from.value - to.min;
    const toPosition = to.value - to.min;
    controlSlider.style.background = `linear-gradient(
      to right,
      ${sliderColor} 0%,
      ${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,
      ${rangeColor} ${((fromPosition)/(rangeDistance))*100}%,
      ${rangeColor} ${(toPosition)/(rangeDistance)*100}%,
      ${sliderColor} ${(toPosition)/(rangeDistance)*100}%,
      ${sliderColor} 100%)`;
}

function setToggleAccessible(currentTarget) {
  const toSlider = document.querySelector('#toSlider');
  if (Number(currentTarget.value) <= 0 ) {
    toSlider.style.zIndex = 2;
  } else {
    toSlider.style.zIndex = 0;
  }
}

const fromSlider = document.querySelector('#fromSlider');
const toSlider = document.querySelector('#toSlider');
const fromInput = document.querySelector('#fromInput');
const toInput = document.querySelector('#toInput');
fillSlider(fromSlider, toSlider, '#C6C6C6', '#25daa5', toSlider);
setToggleAccessible(toSlider);

fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromInput);
toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toInput);
fromInput.oninput = () => controlFromInput(fromSlider, fromInput, toInput, toSlider);
toInput.oninput = () => controlToInput(toSlider, fromInput, toInput, toSlider);

$(document).ready(function(){
  $('[data-bs-toggle="popover"]').popover();
});

