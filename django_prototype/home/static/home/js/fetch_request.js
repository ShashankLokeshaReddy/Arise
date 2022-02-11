

$(function () {
    $('#order-selection-date').on('change', function (e) {
        e.preventDefault();
        let date = $('#order-selection-date').val();
        if (date === "") {
            alert("Please enter a date") // TODO USE GOOD TEXTBOX AND NOT AN ALERT
        } else {
            $.ajax({
                    url: "/db",
                    method: "GET",
                    data: {date: date},
                    success: function (data) {
                        $('#testContainer').append(`<div><label id="addLabel" for="name">${data['selected_date']}</label></div>`);
                    },
                    error: function (data) {
                        alert(data.toString())
                    }
                }
            );

        }
    });
})