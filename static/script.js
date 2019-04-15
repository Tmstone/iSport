$(document).ready(function() {
     $('#rBtn').click(function(){
          $('.rForm').toggle();
     })
     $('#lBtn').click(function(){
          $('.lForm').toggle();
     })
     $.get('user/first_name', function(firstName){
          $('#first-name').html(firstName)
     })
     $.get('/nav', function(nav){
          $('#nav').html(nav)
     })
})
