$(document).ready(function() {
     $.get('user/first_name', function(firstName){
          $('#first-name').html(firstName)
          console.log(firstName);
     })
     $.get('/nav', function(nav){
          $('#nav').html(nav)
     })
     $('#rBtn').click(function(){
          $('.rForm').toggle();
     })

})
