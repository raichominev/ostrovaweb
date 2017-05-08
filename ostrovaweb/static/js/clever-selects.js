$(document).ready(function() {
    $.fn.loadChildChoices = function(child) {
        var valuefield = child;
        var ajax_url = valuefield.attr('ajax_url');
        var empty_label = valuefield.attr('empty_label') || '--------';

        $.get(
            ajax_url,
            {
                field: valuefield.attr('name'),
                parent_field: $(this).attr('name'),
                parent_value: $(this).val(),
                add_rel_field: valuefield.attr('additional_related_field'),
                add_rel_value: $('#' + valuefield.attr('additional_related_field')).val()
            },
            function(j) {
                var options = '';
                    options += '<option value="">' + empty_label + '</option>';

                for (var i = 0; i < j.length; i++) {
                    options += '<option value="' + j[i][0] + '">' + j[i][1] + '</option>';
                }
                valuefield.html(options);
                valuefield.trigger('change');
                valuefield.trigger("liszt:updated"); // support for chosen versions < 1.0.0
                valuefield.trigger("chosen:updated"); // support for chosen versions >= 1.0.0
            },
            "json"
        );
    };

    $.fn.loadAllChainedChoices = function() {
        var chained_ids = $(this).attr('chained_ids').split(",");

        for (var i = 0; i < chained_ids.length; i++) {
            var chained_id = chained_ids[i];

            $(this).loadChildChoices($('#' + chained_id));
        }
    };

    $('.chained-parent-field').change(function() {
        $(this).loadAllChainedChoices();
    });
//    }).change();  // Use change only if really necessary. Be aware of using it in POST requests!

     Suit.after_inline.register('clever-selects-inline-dynamic', function(inline_prefix, row){

            $('.chained-parent-field').change(function() {
                                               $(this).loadAllChainedChoices();
                                           //});
                                           }).change();

            console.info(inline_prefix)
            console.info(row)
     });

});