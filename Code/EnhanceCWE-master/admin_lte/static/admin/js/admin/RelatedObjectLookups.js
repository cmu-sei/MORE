// Handles related-objects functionality: lookup link for raw_id_fields
// and Add Another links.

function html_unescape(text) {
    // Unescape a string that was escaped using django.utils.html.escape.
    text = text.replace(/&lt;/g, '<');
    text = text.replace(/&gt;/g, '>');
    text = text.replace(/&quot;/g, '"');
    text = text.replace(/&#39;/g, "'");
    text = text.replace(/&amp;/g, '&');
    return text;
}

// IE doesn't accept periods or dashes in the window name, but the element IDs
// we use to generate popup window names may contain them, therefore we map them
// to allowed characters in a reversible way so that we can locate the correct
// element when the popup window is dismissed.
function id_to_windowname(text) {
    text = text.replace(/\./g, '__dot__');
    text = text.replace(/\-/g, '__dash__');
    return text;
}

function windowname_to_id(text) {
    text = text.replace(/__dot__/g, '.');
    text = text.replace(/__dash__/g, '-');
    return text;
}

function showAdminPopup(triggeringLink, name_regexp) {
    var name = triggeringLink.id.replace(name_regexp, '');
    name = id_to_windowname(name);
    var href = triggeringLink.href;
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    // ADMIN LTE CUSTOM: changed width
    var win = window.open(href, name, 'height=500,width=1000,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function showRelatedObjectLookupPopup(triggeringLink) {
    return showAdminPopup(triggeringLink, /^lookup_/);
}

function dismissSearchRelatedLookupPopupMulti(win, selected) {
    // Used when the search lookup exits by selecting multiple records using checkboxes
    var name = windowname_to_id(win.name);
    var elem = $("#" + name);

    if (elem.parents('.autocomplete-light-widget').hasClass('single')) {
        if (selected.length > 0) {
            var id = selected[0]['id']
            var reprName = selected[0]['name']

            if ($(elem).is('select')) {
                var o = new Option(reprName, id);
                elem.get(0).options[elem.get(0).options.length] = o;
                o.selected = true;
            }
        }


    } else if (elem.parents('.autocomplete-light-widget').hasClass('multiple')) {
        for (i = 0; i < selected.length; i++)  {
            var id = selected[i]['id']
            var reprName = selected[i]['name']

            if ($(elem).is('select')) {
                var o = new Option(reprName, id);
                elem.get(0).options[elem.get(0).options.length] = o;
                o.selected = true;
            }
        }

    } else if (elem.get(0).type == "select-multiple") {
        var values = elem.val();
        for (i = 0; i < selected.length; i++)  {
            values.push(selected[i]['id']);
        }
        elem.val(values)


    } else if (elem.get(0).type == "select-one") {

        elem.val(selected[0]['id']);
    }

    // ADMIN LTE CUSTOM: element focus
    //elem.focus();
    win.close();
}

function dismissSearchRelatedLookupPopupSingle(win, reprName, chosenId) {
    // Used when search lookup exits by clicking on the link of and entry
    var name = windowname_to_id(win.name);
    var elem = $("#" + name);

    if (elem.parents('.autocomplete-light-widget').length) {

        if ($(elem).is('select')) {
            var o = new Option(reprName, chosenId);
            elem.get(0).options[elem.get(0).options.length] = o;
            o.selected = true;
        }

    } else if (elem.get(0).type == "select-multiple") {
        var values = elem.val()
        values.push(chosenId)
        elem.val(values)

    } else if (elem.get(0).type == "select-one") {
        elem.val(chosenId);
    }
    // ADMIN LTE CUSTOM: element focus
    //elem.focus();
    win.close();
}


function dismissRelatedLookupPopup(win, chosenId) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
        elem.value += ',' + chosenId;
    } else {
        document.getElementById(name).value = chosenId;
    }
    // ADMIN LTE CUSTOM: element focus
    //elem.focus();
    win.close();
}

function showRelatedObjectPopup(triggeringLink) {
    // ADMIN LTE CUSTOM: replacing 'search'
    var name = triggeringLink.id.replace(/^(change|add|delete|search)_/, '');
    name = id_to_windowname(name);
    var href = triggeringLink.href;
    // ADMIN LTE CUSTOM: changed width
    var win = window.open(href, name, 'height=500,width=1000,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function dismissAddRelatedObjectPopup(win, newId, newRepr) {
    // newId and newRepr are expected to have previously been escaped by
    // django.utils.html.escape.
    newId = html_unescape(newId);
    newRepr = html_unescape(newRepr);
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    var o;
    if (elem) {
        var elemName = elem.nodeName.toUpperCase();
        if (elemName == 'SELECT') {
            o = new Option(newRepr, newId);
            elem.options[elem.options.length] = o;
            o.selected = true;
        } else if (elemName == 'INPUT') {
            if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
                elem.value += ',' + newId;
            } else {
                elem.value = newId;
            }
            // ADMIN LTE CUSTOM: element focus
            //elem.focus();
        }
        // Trigger a change event to update related links if required.
        django.jQuery(elem).trigger('change');
    } else {
        var toId = name + "_to";
        o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    win.close();
}

function dismissChangeRelatedObjectPopup(win, objId, newRepr, newId) {
    objId = html_unescape(objId);
    newRepr = html_unescape(newRepr);
    var id = windowname_to_id(win.name).replace(/^edit_/, '');
    var selectsSelector = interpolate('#%s, #%s_from, #%s_to', [id, id, id]);
    var selects = django.jQuery(selectsSelector);
    selects.find('option').each(function() {
        if (this.value == objId) {
            this.innerHTML = newRepr;
            this.value = newId;
        }
    });
    win.close();
};

function dismissDeleteRelatedObjectPopup(win, objId) {
    objId = html_unescape(objId);
    var id = windowname_to_id(win.name).replace(/^delete_/, '');
    var selectsSelector = interpolate('#%s, #%s_from, #%s_to', [id, id, id]);
    var selects = django.jQuery(selectsSelector);
    selects.find('option').each(function() {
        if (this.value == objId) {
            django.jQuery(this).remove();
        }
    }).trigger('change');
    win.close();
};

// Kept for backward compatibility
showAddAnotherPopup = showRelatedObjectPopup;
dismissAddAnotherPopup = dismissAddRelatedObjectPopup;
