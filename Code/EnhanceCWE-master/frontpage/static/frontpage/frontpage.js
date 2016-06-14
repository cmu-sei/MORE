jQuery(function() {
    var cwe_select = $("#id_cwes");
    var page_limit = cwe_select.data('page-limit');

    // Make CWE selection a multiple ajax select2
    cwe_select.select2({
        placeholder: "Search CWEs",
        ajax: {
            url: $(this).data('ajax-url'),
            dataType: 'json',
            delay: 250,
            data: function (params) {
              return {
                  q: params.term, // search term
                  page: params.page
              };
            },

            processResults: function (data, params) {
              // parse the results into the format expected by Select2.
              // since we are using custom formatting functions we do not need to
              // alter the remote JSON data
                params.page = params.page || 1;
                return {
                    results: data.items,
                    pagination: {
                        more: (params.page * page_limit) < data.total_count
                    },
                };
            },
            cache: true
        },
        minimumInputLength: 0,
    });

    $('#cwe-submit-button').on('click', function(event){
        $('#marquee').slideUp();
        $('.muo-search-container').show();

        // Prevent the default django action on button click. Otherwise it'll reload the whole page
        event.preventDefault();

        // Get the selected CWE ids
        var selected_cwes = $('#id_cwes').val();

        // If none of the CWEs are selected, the value of the selected_cwes will be null. I such cases, we need to mimic
        // the default behaviour. We will send an empty array in the ajax request and display all the misuse cases.
        if (selected_cwes == null) {
            selected_cwes = [];
        }

        // Load the misuse cases for the selected cwes
        load_misusecases(selected_cwes)
    });


    $("body").on('click', '.misuse-case-container', function(){
        // get the misuse case id of the clicked misuse case
        var misuse_case_id = $(this).attr("data-value");

        // get the misuse case id of the last selected misuse case
        var last_selected_misuse_case_id = $('.misuse-case-container.selected').attr("data-value");

        // If the selected misuse case is clicked again, do nothing, otherwise send the ajax
        // request to get the use cases corresponding to the clicked misuse case
        if (misuse_case_id != last_selected_misuse_case_id) {
            // Remove the selection from the last selected misuse case div
            $('.misuse-case-container.selected').removeClass('selected');

            // Select the current div
            $(this).addClass('selected');

            // Load usecases corresponding to the selected misuse
            load_usecases(misuse_case_id);
        }
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


    $("body").on('click', '#muo_see_more', function(e){
        // stop propagating the click event to misuse-case-container
        e.stopPropagation();

        var misuse_case_id = $(this).attr("data-value");
        var hidden_attributes = $('#hidden_attributes' + misuse_case_id);

        if (!hidden_attributes.is(':visible')){
            hidden_attributes.slideDown();
            $(this).text('See Less');
        } else {
            hidden_attributes.slideUp();
            $(this).text('See More');
        }
    });


    $(document).on('keypress', '#filter_misuse_case', function(e){
        if(e.which == 13) {
            var search_term = $(this).val();
            var selected_cwes = $('#id_cwes').val();

            if (selected_cwes == null) {
                selected_cwes = [];
            }
            load_misusecases(selected_cwes, search_term)
        }
    });

});



function load_usecases(misuse_case_id) {
    $.ajax({
        url: 'get_usecases/',
        type: 'POST',
        data: {misuse_case_id: misuse_case_id}, // Send the selected misuse case id

        success: function(result) {
            // If ajax call is successful, reload the fat-scroll-div which contains the use cases
            $('.fat-scroll-div').replaceWith(result);
        },

        error: function(xhr,errmsg,err) {
            // Show error message in the alert
            alert("Oops! We have encountered and error \n" + errmsg);
        }
    });
}


function load_misusecases(cwe_ids, search_term) {
    $.ajax({
        url: 'get_misusecases/',
        type: 'POST',
        data: {cwe_ids: cwe_ids, search_term: search_term},

        success: function(result) {
            // If ajax call is successful, reload the slim-scroll-div which contains the misuse cases
            $('.slim-scroll-div').replaceWith(result);

            // If misuse cases found in the system
            if ($('.misuse-case-container').length)
            {
                // Select the first misuse case by default
                first_misuse_case_div = $($('.misuse-case-container').get(0));

                first_misuse_case_div.addClass('selected');

                // Get the misuse case id of the first misuse case
                misuse_case_id = first_misuse_case_div.attr("data-value");

                load_usecases(misuse_case_id);

            } else {
                $('.use-case-container').hide();
            }

            var misuse_case_filter = $('#filter_misuse_case');
            misuse_case_filter.focus().val(misuse_case_filter.val());
        },

        error: function(xhr,errmsg,err) {
            // Show error message in the alert
            alert("Oops! We have encountered and error \n" + errmsg);
        }
    });
}