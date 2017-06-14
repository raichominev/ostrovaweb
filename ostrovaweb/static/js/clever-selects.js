$(document).ready(function() {

    $.fn.getType = function(){ return this[0].tagName == "INPUT" ? this[0].type.toLowerCase() : this[0].tagName.toLowerCase(); }

    $.fn.loadChildChoices = function(child) {
        var valuefield = child;
        var parent = $(this);
        var ajax_url = valuefield.attr('ajax_url');
        var additional_custom_function = valuefield.attr('additional_custom_function');
        var empty_label = valuefield.attr('empty_label') || '--------';

        var field = valuefield.attr('name');
        var parent_field = $(this).attr('name');
        var parent_value = $(this).val();

        //this is when using select2 multiple widget for a single value
        if (Object.prototype.toString.call( parent_value ) === '[object Array]' ) {
           parent_value = parent_value[0];
        }

        var add_rel_field = valuefield.attr('additional_related_field');
        var add_rel_value = $('#' + valuefield.attr('additional_related_field')).val();

        $.get(
            ajax_url,
            {
                field: field,
                parent_field: parent_field,
                parent_value: parent_value,
                add_rel_field: add_rel_field,
                add_rel_value: add_rel_value
            },
            function(j) {
                if (valuefield.getType() == "select") {
                    var options = '';
                        options += '<option value="">' + empty_label + '</option>';

                    for (var i = 0; i < j.length; i++) {
                        options += '<option value="' + j[i][0] + '">' + j[i][1] + '</option>';
                    }
                    valuefield.html(options);
                } else if (valuefield.getType() == "text") {
                    var txt = '';
                    for (var i = 0; i < j.length; i++) {
                        txt += j[i][1] + ' ';
                    }
                    txt = txt.replace(/ +$/, '');  //strip last space, which is necessary for numeric fields
                    valuefield.val(txt);

                } else if (valuefield.getType() == "img") {
                    var txt = '';
                    for (var i = 0; i < j.length; i++) {
                        txt += j[i][1] + ' ';
                    }
                    txt = txt.replace(/ +$/, '');  //strip last space, which is necessary for numeric fields
                    valuefield.attr('src', txt);

                } else {
                    var txt = '';
                    for (var i = 0; i < j.length; i++) {
                        txt += j[i][1] + ' ';
                    }
                    txt = txt.replace(/ +$/, '');  //strip last space, which is necessary for numeric fields
                    valuefield.val(txt);

                }

                valuefield.trigger('change');
                valuefield.trigger("liszt:updated"); // support for chosen versions < 1.0.0
                valuefield.trigger("chosen:updated"); // support for chosen versions >= 1.0.0

                if(additional_custom_function in $.fn) {
                    $.fn[additional_custom_function](field, parent_field, parent_value, add_rel_field, add_rel_value, valuefield, parent);
                }
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