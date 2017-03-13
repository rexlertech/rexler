$(document).ready(function() {
    pic_width = $('#profile-pic-container').parent().width();
    $('#profile-pic-container').height(pic_width);
    $('#profile-pic-container').width(pic_width);
    $('.alert-pic-preview').height($('.alert-pic-preview>img').width());

    //redirect to main page when user search
    var redirect_to_main = localStorage.getItem('redirect_to_main');
    if (redirect_to_main === 'true') {
        min_age = localStorage.getItem('min_age');
        max_age = localStorage.getItem('max_age');
        country = localStorage.getItem('country');
        id = localStorage.getItem('id');
        getClientList(min_age, max_age, country, id);
        $('#id_seaminage').val(min_age);
        $('#id_seamaxage').val(max_age);
        $('#id_seacountry').val(country);
        $('#client_list_id').val(id);
        localStorage.setItem('redirect_to_main', 'false');
        localStorage.removeItem('min_age');
        localStorage.removeItem('max_age');
        localStorage.removeItem('country');
        localStorage.removeItem('id');
    }

    var quan = $("#alertsquantity").text();
    if (quan > 0) {
        $("#alertsquantity").show();
    } else {
        $("#alertsquantity").hide();
    }

    quan = $("#count_inbox").text();
    if (quan > 0) {
        $("#count_inbox").show();
    } else {
        $("#count_inbox").hide();
    }

    resize_preview();
});

$(window).resize(function() {
    resize_preview();
});

$(window).trigger('resize');

//Open advanced search
function advanced_search(divId) {
    $("#" + divId).toggle();
}

$("#div_id_seaminage").change(function() {
    $('#search-error').empty();
});
$("#div_id_seamaxage").change(function() {
    $('#search-error').empty();
});
$("#div_id_seacountry").change(function() {
    $('#search-error').empty();
});

//Avoid search dropdown closing when clicked
$('.span-search').on('click', function(event) {
    $('.dropdown-menu').parent().toggleClass('open');
});

//close search dropdown when user click outsite
$('body').on('click', function(e) {
    if (!$('.span-search').is(e.target) &&
        $('.span-search').has(e.target).length === 0 &&
        $('.open').has(e.target).length === 0
    ) {
        $('.btn-group').removeClass('open');
    }
});

//Modal instead of Dropdown
if ($(window).width() <= 576) {
    $(".dropdown-menu").remove();
    $('#menu-search').click(function() {
        $("#modal-search").modal('show');
    });
    $('#menu-feelings').click(function() {
        $("#modal-feelings").modal('show');
    });
    $('#menu-alerts').click(function() {
        updateAlerts();
        $("#alertsquantity").text(0).hide();
        $("#modal-alerts").modal('show');
    });
    $('#menu-profile').click(function() {
        $("#modal-profile").modal('show');
    });
} else {
    $('#menu-alerts').click(function() {
        updateAlerts();
        $("#alertsquantity").text(0).hide();
    });
}

function updateAlerts() {
    $.ajax({
        url: '/ajax/update/noti/',
        dataType: 'json',
        type: 'POST',
        data: {
            'quantity': 5
        },
        success: function(data) {
            if (data['error'] == 'yes') {
                alert(data["description"]);
            }
        }
    });
}
//load items for pagination calling ajax function
function show_more(url) {
    $('.membersContainer').scrollPagination({
        'contentPage': url, // the url you are fetching the results
        'contentData': {},
        'scrollTarget': $(window),
        'heightOffset': 10,
        'beforeLoad': function() {
            // before load function, you can display a preloader div
            $('#loading').fadeIn();
        },
        'afterLoad': function(elementsLoaded) {
            $('#loading').fadeOut();
            if ($('#members-content').children().size() > 12) {
                // if more than 12 results already loaded, then stop pagination
                $('#nomoreresults').fadeIn();
                $('#members-content').stopScrollPagination();
            }
            resize_preview();
        }
    });
}

//Read data from search inputs
function read_data() {
    var json = {};
    min_age = $('#id_seaminage').val();
    max_age = $('#id_seamaxage').val();
    country = $('#id_seacountry option:selected').val();
    list_id = $('#client_list_id').val();
    json.data = [];
    json.data.push({
        min_age: $('#id_seaminage').val()
    });
    json.data.push({
        max_age: $('#id_seamaxage').val()
    });
    json.data.push({
        country: $('#id_seacountry option:selected').val()
    });
    json.data.push({
        list_id: $('#client_list_id').val()
    });

    return json.data;
}

//Do the search
function simple_search(e, url) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var min_age = $('#id_seaminage').val();
    var max_age = $('#id_seamaxage').val();
    var country = $('#id_seacountry option:selected').val();
    var id = '';
    if (window.location.pathname != url) {
        localStorage.setItem('redirect_to_main', 'true');
        localStorage.setItem('min_age', min_age);
        localStorage.setItem('max_age', max_age);
        localStorage.setItem('country', country);
        localStorage.setItem('id', id);
        window.location.replace(url);
    } else {
        getClientList(min_age, max_age, country, id);
    }
}

//Show client list after ajax request
function showClientList(json_members, clr_result = false) {
    if (json_members['error'] != null) {
        $('#search-error').addClass('search-error');
        $('#search-error').html("<label class='no_results'>" + json_members['error'] + "</label>");
        $('#search-btn-group').addClass('open');
    } else {
        client_list = JSON.parse(json_members);
        var cad = $("#client_list_id").val();
        var clase = $('div[name]').first().attr('class');
        if (clr_result) {
            $('#members-content').empty();
        }
        $('#search-error').empty();
        for (var member in client_list) {
            var id = client_list[member].pk;
            cad = (cad == "" ? id : cad + "," + id);
            html = '<div name="list_members" class="' + clase + '">';
            html += '<div class="profile-preview">';
            html += '<div class="profile-member"><a href="/profile/' + client_list[member].fields.cliusername + '">'
            html += '<img class="pic-profile" src="' + client_list[member].fields.profile_picture + '" />';
            html += '</a></div>';
            if (client_list[member].fields.feecode != null) {
                html += '<div class="feel">';
                html += '<img src="' + client_list[member].fields.feecode + '" />';
                html += '</div>';
            }
            html += '<div class="row extra-pictures">';
            if (client_list[member].fields.client_gallery.length != 0) {
                for (var i = 1; i <= client_list[member].fields.client_gallery.length; i++) {
                    html += '<div class="col-xs-3 gallery-preview">';
                    html += '<img src="' + client_list[member].fields.client_gallery[i - 1] + '" class="item-preview"/>';
                    if (i === 4 && client_list[member].fields.client_gallery.length > 4) {
                        html += '<div class="column"><div class="container"><label>+' + (client_list[member].fields.client_gallery.length - 4) + '</label></div></div>'
                    }
                    html += '</div>'
                    if (i === 4)
                        break;
                }
            }
            html += '</div>';
            html += '<div class="row profile-info">';
            html += '<div class="col-md-9">';
            html += '<strong>';
            html += '<a href="/profile/' + client_list[member].fields.cliusername + '">';
            html += '<b>@' + client_list[member].fields.cliusername + '</b>';
            html += '</a>';
            if (client_list[member].fields.clibirthdate != null) {
                html += ', ' + client_list[member].fields.age;
            }
            html += '</strong>'
            if (client_list[member].fields.cliname != null) {
                html += '<br />' + client_list[member].fields.cliname;
            }
            if (client_list[member].fields.citcode != null) {
                html += '<br />' + client_list[member].fields.citcode;
            }
            html += '</div>';
            html += '<div class="col-md-3 hidden-sm-down">';
            html += '<img id="iconchat_' + client_list[member].pk + '" src="/static/dateSite/img/chat_icon.png" class="action-icons"/>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
            $("#members-content").append(html);
        }
        $("#client_list_id").val(cad);
        $('.btn-group').removeClass('open');
        $('#modal-search').modal('hide');
    }
}


// client list gallery images preview
function resize_preview() {
    if ($(window).width() > 767) {
        if ($('.profile-member').length != 0) {
            item_width = $('.item-preview').width();
            $('.gallery-preview').height(item_width);
            $('.item-preview').height(item_width);

            $('.item-preview').each(function() {
                if ($(this).height() != item_width) {
                    $(this).css('width', 'auto');
                }
            });

            profile_width = $('.profile-preview > div').width();
            $('.profile-member').height(profile_width);

            $('.pic-profile').each(function() {
                if ($(this).height() < $('.profile-member').height()) {
                    $(this).height($('.profile-member').height());
                    $(this).css('width', 'auto');
                }
            });
        }
        $('.profile-data').css('height', $('.profile-top').height());
    }
    if (document.getElementById('edit-profile') != null) {
        if ($('#profile-view').width() < 520) {
            $('.picture-update').removeClass('col-md-4');
            $('.picture-update').addClass('col-md-12');
            $('.edit-details').removeClass('col-md-8');
            $('.edit-details').addClass('col-md-12');
            $('.column-edit').removeClass('col-md-6');
            $('.column-edit').addClass('col-md-12');
        } else {
            $('.picture-update').removeClass('col-md-12');
            $('.picture-update').addClass('col-md-4');
            $('.edit-details').removeClass('col-md-12');
            $('.edit-details').addClass('col-md-8');
            $('.column-edit').removeClass('col-md-12');
            $('.column-edit').addClass('col-md-6');
        }
    }
}
