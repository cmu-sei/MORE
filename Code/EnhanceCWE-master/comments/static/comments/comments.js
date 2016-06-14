jQuery(function() {

    //Submit the form on pressing enter (key 13), but not while holding space
    $("body").on('keypress', 'textarea[id=id_comment]', function() {
        if ((event.which == 13) && !event.shiftKey) {
            var form = $(this).parents('form:first');
            form.submit();
            return false;
        }
    });

    // Delete comment using Ajax call
    $("body").on('click', 'a.delete-comment', function(){
        // Prevent the default django action on button click. Otherwise it'll reload the whole page
        event.preventDefault();

        var comment_id = $(this).data('value');
        var url = $(this).data('ajax-url');

        $.ajax({
            url: url,
            type: 'POST',
            data: {comment_id: comment_id}, // Send the selected use case id

            success: function(result) {
                if (result.is_removed) {
                    var comment = $("#c" + result.comment_id);
                    comment.hide("normal",function(){
                        comment.remove();
                    })
                } else {
                    alert("Oops! Could not delete the comment!")
                }
            },

            error: function(xhr,errmsg,err) {
                // Show error message in the alert
                alert("Oops! We have encountered and error \n" + errmsg);
            }
        });

    });
});
