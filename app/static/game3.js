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
    socket.emit("Update param for Game3", {'id': event.target.id, 'value': event.target.value});
    console.log('in input')
})


socket.on('G3 take session data', (msg)=>{
    console.log('Updating g3 data')
    $('#options').val(msg['data']['options']);
    $('#TR').val(msg['data']['TR']);
    $('#TE').val(msg['data']['TE']);
    $('#FA').val(msg['data']['FA']);
    console.log(msg['data'])
})
$(document).ready(function(){
  $('[data-bs-toggle="popover"]').popover();
});

$('.carousel').carousel({
  interval: false,
});