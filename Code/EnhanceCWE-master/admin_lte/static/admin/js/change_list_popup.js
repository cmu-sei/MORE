django.jQuery(function($){

    var container = $(document);

    //Deactivate onClick action provided by django
    container.find('#result_list tbody a').each(function () {
        $(this).removeAttr('onclick');
    });

    //Activate/Deactivate submit button according to checkbox selection
    container.on('click', 'tr input.action-select, input#action-toggle', function(event){
        if ($("tr input.action-select:checked").length > 0) {
            $("#add_selected").removeAttr("disabled");
        } else {
            $("#add_selected").attr("disabled", "disabled");
        }
    });

    // When selecting checkboxes and clicking on 'Add Selected'
    container.on('click', '#add_selected', function(event){
        var selected = [];

        $("tr input.action-select:checked").each(function () {
            //Read name from the first anchor field in the row
            var name = $(this).parents("tr").find("a").get(0).text;
            var id = $(this).val();
            selected.push({'id': id, 'name': name});
        });
        if (selected.length) {
            opener.dismissSearchRelatedLookupPopupMulti(window, selected);
        }
        event.preventDefault();
    });

    // On clicking on an object link
    container.on('click', '#result_list tbody a', function(event){
        //Read value from the checkbox in the same row
        var id = $(this).parents("tr").find("input.action-select").val();
        var name = this.text
        opener.dismissSearchRelatedLookupPopupSingle(window, name, id);

        event.preventDefault();
    });

});