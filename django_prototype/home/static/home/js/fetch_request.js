

async function showUserInConsole() {
    const response = await fetch("static/home/user.json");
    const user = await response.json();

    console.log(user);
}

showUserInConsole();

$(function(){
     $('#testJquery').on('click', function(e){
         console.log('helo')
         e.preventDefault();
         let date = document.getElementById("order-selection-date").value;
         // let date = $('#order-selection-date').val()
         if (date === ""){
             alert("Please enter a date") // TODO USE GOOD TEXTBOX AND NOT AN ALERT
         }else{
             console.log("Read in date: " + date)
             if(!$('#addLabel').length){
                $('#testContainer').append('<div><label id="addLabel" for="name">Datum eingegeben </label></div>')
             }else{
                 $('#addLabel').remove();
             }

             $.ajax({
                 url: "/db",
                 method: "GET",
                 success: function(data){
                     console.log("success")
                     $('#testContainer').append('<div><label id="addLabel" for="name"></label></div>');
                     $('#addLabel').html(data);
                 },
                 error:function(data){
                     alert(data.toString())
                 }
             }
             );

         }
     });
})