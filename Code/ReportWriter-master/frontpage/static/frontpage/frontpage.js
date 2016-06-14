jQuery(function() {

    if ($('#search-reports-input').val()) {
        $('#marquee').slideUp();
        search_reports();
    }

    $('#search-reports-form').on('submit', function(event){
        // Prevent the default django action on button click. Otherwise it'll reload the whole page
        event.preventDefault();
        search_reports();
    });


    $("#muo-modal").on("show.bs.modal", function (e) {
        var usecase_id = $(e.relatedTarget).data('usecase-id');
        var url = $(e.relatedTarget).data('ajax-url');

        // Load the report issue dialog
        $.ajax({
            url: url,
            type: 'POST',
            data: {usecase_id: usecase_id}, // Send the selected use case id

            success: function(result) {
                $(e.currentTarget).html(result);
            },

            error: function(xhr,errmsg,err) {
                // Show error message in the alert
                alert("Oops! We have encountered and error \n" + errmsg);
            }
        });
    });

});


function search_reports(){
    $('#marquee').slideUp();
    $('.search-reports-container').show();

    $.ajax({
        url: $('#search-reports-form').data('ajax-url'),
        type: 'POST',
        data: {term: $('#search-reports-input').val()}, // Send the search term

        success: function(result) {
            $('.search-reports-result').html(result);
        },

        error: function(xhr,errmsg,err) {
            // Show error message in the alert
            alert("Oops! We have encountered and error \n" + errmsg);
        }
    });
}

