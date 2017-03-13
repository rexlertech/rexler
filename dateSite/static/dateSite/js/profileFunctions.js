$(window).resize(function() {
    resize_album_preview();
    var w_chat = $(window).width();
    if ($(window).width() > 767) {
        if ($('#chatContainer').hasClass('chatContainerChat')) {
            w_chat = 'calc(100% - ' + 510 + 'px)';
        } else {
            w_chat = 'calc(100% - ' + 240 + 'px)';
        }
    }
    $('.profile').css({
        'width': w_chat
    });
    collage();
});
$(window).trigger('resize');

$(document).ready(function(e) {
    if (private_collection != null) {
        array_collection = private_collection.replace(/[\[\] ]+/g, '').split(',');
    }
    is_me = (user_pk == client_code ? true : false);

    $('#profile_percentage').attr('value', percentage);
    albums_member(o_album_list);
    baguetteBox.run('.thumbs-preview', {
        buttons: true,
        fullScreen: false,
        onChange: function(currentIndex, imagesCount) {
            if (is_me && !$(e.target).attr('type')) {
                make_profile_picture_link(currentIndex);
            }
        },
    });
    viewer_height = $(window).height();
    if ($(window).height() > 360) {
        viewer_height = Math.floor($('.profile').height() * 0.50);
    }
    $('.profile-top').height(viewer_height);


    if ($(window).width() > 767) {
        $('.profile-albums').height(viewer_height);
    }
    if ($(window).width() > 992) {
        var w = $(window).width() - $('.profile').width() - $('.chatContainer').width() - 50;
        $('#members-content').width(w);
        show_suggestions(url_clients);
    }
    resize_album_preview();
});

$(document).on('click', '.photo-gallery', function(e) {
    var album_id, is_private;
    var click_id = e.target.id;
    if ($(this).attr('type') === '2' || $(this).children().attr('type') === '2') {
        is_private = true;
        album_id = ($(this).attr('data-album-id') != null ? $(this).attr('data-album-id') : $(this).attr('id'))
    }
    if (!is_me && is_private && array_collection.indexOf(album_id) === -1) {
        view_private_album(album_id, click_id)
    } else {
        show_thumbs_gallery(e.target.id);
    }
});

$(document).on('click', '.thumb', function(e) {
    e.preventDefault();
});

$(document).on('click', '.make-profile', function(e) {
    $('#profileModal').modal('show');
    $('.modal-backdrop').css({
        'display': 'none'
    });
    $("#profileYes").click(function() {
        $.ajax({
            type: 'POST',
            url: profilepic_url,
            data: {
                'picture_id': e.target.id,
            },
            success: function(data) {
                $('#profileModal').modal('hide');
                $('#close-button').trigger("click");
                $('#picture-preview').attr('src', '/media/' + data.pic);
                $('#menu-profile-pic').attr('src', '/media/' + data.pic);
                $('#dropmenu-profile-pic').attr('src', '/media/' + data.pic);
                resize_album_preview();

                //traer de nuevo el album del cliente
                $.ajax({
                    type: 'POST',
                    url: getalbum_url,
                    cache: false,
                    data: {
                        'albumid': data.albumid
                    },
                    success: function(results) {
                        show_thumbs_gallery('img-' + data.album, results);
                    }
                });
            },
            error: function() {
                console.log('Error to try make the profile picture');
            },
        });
    });
});

$(document).on('click', '#add-album', function(e) {
    $('#uploadAlbumModal').modal('show');
});

$(document).on('click', '.show-pictures', function(e) {
    $('#profilepicturesModal').modal('show');
    $("#btnYes").click(function() {
        if ($('.fill-pic [data-value="selected"]').attr('id') == null) {
            $('#msg').html("You haven't selected any picture yet");
            $('#body-select-pic').scrollTop(0);
        } else {
            $.ajax({
                type: 'POST',
                url: profilepic_url,
                data: {
                    'picture_id': $('.fill-pic [data-value="selected"]').attr('id'),
                },
                success: function(data) {
                    $('#profilepicturesModal').modal('hide');
                    $('.pic-edit > img').attr('src', '/media/' + data.pic);
                    $('#menu-profile-pic').attr('src', '/media/' + data.pic);
                    $('#dropmenu-profile-pic').attr('src', '/media/' + data.pic);
                },
                error: function() {
                    console.log('Error get the pictures public albums');
                },
            });
        }
    });
    $('#btnCancel').click(function() {
        $('.fill-pic').css({
            'border': '2px solid #FFF',
            'box-shadow': 'none'
        });
    });
});

$(document).on('click', '.thumb-prev', function(e) {
    $('#msg').empty();
    $('.fill-pic').css({
        'border': '2px solid #FFF',
        'box-shadow': 'none'
    });
    $('.fill-pic > img').attr('data-value', 'none');
    $(e.target).closest("div").css({
        'border': '2px solid #07c',
        'box-shadow': '0 0 10px #07c'
    });
    $(e.target).attr('data-value', 'selected');
});

$(document).on('click', '.qq-upload-button', function() {
    $('#error-msg').empty();
    $('#error-msg').hide();
});

$('a#info_link').click(function(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#basic_info').show();
});

$('a#physical_link').click(function(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#physical_description').show();
});

$('a#work_link').click(function(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#work_education').show();
});

$('a#hobbies_link').click(function(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#hobbies').show();
});

$('a#pass_link').click(function(e) {
    e.preventDefault();
    $('.container-box > div').hide();
    $('#change_pass').show();
});

$("#btn-create-album").click(function() {
    if (pictures_to_upload.length == 0) {
        $('#error-msg').html("<label>You haven't selected any pictures</label>");
        $('#error-msg').show();
    } else {
        uuid_list = []
        for (pic in pictures_to_upload) {
            uuid_list.push(pictures_to_upload[pic].uuid);
        }
        $.ajax({
            type: 'POST',
            url: createalbum_url,
            data: {
                'album_name': $('#id_phaname').val(),
                'album_type': $('#id_phatype option:selected').val(),
                'album_description': $('#id_phadescription').val(),
                'pictures[]': uuid_list,
            },
            success: function(data) {
                $('#image_preview ').empty();
                $('#uploadAlbumModal').modal('hide');
                get_albums();
                show_thumbs_gallery(data.album);
                pictures_to_upload = [];
            },
            error: function() {
                console.log('error create album');
            }
        });
    }
});

$('#btn-go-top').click(function(e) {
    e.preventDefault();
    $('html,body').animate({
        scrollTop: 0
    }, 'fast');
});

$('#picture-preview').click(function() {
    baguetteBox.run('.profile_picture', {
        buttons: false,
    });
});

$(function() {
    show_more(url_clients);
});

function show_thumbs_gallery(album_id, album_list = o_album_list) {
    album_list = JSON.parse(album_list);
    var id = album_id.replace('title-', '').replace('img-', '');
    var album_type = 1;
    for (var album in album_list) {
        if (album_list[album].album.name == id) {
            html = '<div class="Collage">';
            for (var picture in album_list[album].pictures) {
                html += '<a class="img-thumb" href="/media/' + album_list[album].pictures[picture].picpath + '">';
                html += '<img alt="' + album_list[album].pictures[picture].piccode + '" id="' + album_list[album].pictures[picture].piccode + '" class="thumb" src="/media/' + album_list[album].pictures[picture].picpath + '"';
                if (album_list[album].album.type == '2') {
                    html += ' type="2"';
                    album_type = 2;
                }
                html += '/></a>';
            }
            html += '</div>'
            $("#pictures-box").html(html);
            $('.thumb').hide();
            setTimeout(function() {
                collage();
            }, 100);
            $('.thumb').show();
            baguetteBox.run('.thumbs-preview', {
                buttons: true,
                fullScreen: false,
                titleTag: true,
                onChange: function(currentIndex, imagesCount) {
                    if (album_type != 2 && is_me) {
                        make_profile_picture_link(currentIndex);
                    }
                },
            });
            album_length = album_list[album].pictures.length;
        }
    }
}

function collage() {
    divisor = get_thumb_size(album_length);
    gallery_row_heigth = Math.ceil($('#pictures-box').height() / divisor) + 10;
    $('.Collage').removeWhitespace().collagePlus({
        'targetHeight': gallery_row_heigth,
        'effect': "effect-1",
        'fadeSpeed': 'slow',
        'allowPartialLastRow': false,
    });
}

function albums_member(album_list) {
    $("#albums-box").empty();
    if (album_list) {
        album_list = JSON.parse(album_list);
        if (album_list.length == 0) {
            $("#albums-box").append('<label class="message">No albums to show</label>');
            $('#albums-box').addClass('empty-albums-box');
        }
        for (var album in album_list) {
            if (album_list[album].pictures.length > 0) {
                html = '<div class="col-lg-2 col-md-3 col-xs-4 album-box">';
                html += '<div class="album-preview">';
                html += '<a class="photo-gallery" id="' + album_list[album].album.id + '">'
                html += '<img id="img-' + album_list[album].album.name + '" src="/media/' + album_list[album].pictures[0].picpath + '"';
                if (album_list[album].album.type == '2') {
                    html += 'type="2"';
                    if (!is_me && array_collection.indexOf(album_list[album].album.id.toString()) == -1) {
                        html += ' class="blur"';
                    }
                }
                html += '/></a>'
                if (is_me) {
                    html += '<a href="#" onClick="delete_album(' + album_list[album].album.id + ');" class="delete-album" title="Delete" data-toggle="tooltip">x</a>';
                }
                html += '</div>';
                html += '<label class="album-title"><a class="photo-gallery" id="title-' + album_list[album].album.name + '" data-album-id="' + album_list[album].album.id + '"';
                if (album_list[album].album.type == '2') {
                    html += ' type="2"';
                }
                html += '>' + album_list[album].album.name + '</a></label>';
                html += '</div>';
                $("#albums-box").append(html);
            }
        }
    }
}

function view_private_album(album_id, linkId) {
    $('#privatepicModal').modal('show');
    $('#privatepicModal').on('shown.bs.modal', function(e) {
        e.preventDefault();
        $('#btnYes').unbind('click').click(function() {
            $.ajax({
                type: 'POST',
                url: privatealbum_url,
                data: {
                    album_id: album_id,
                },
                cache: false,
                success: function(data) {
                    json_data = JSON.parse(data);
                    $('#privatepicModal').modal('hide');
                    if (json_data.error != null) //has error
                    {
                        $('#errorModal').modal('show');
                        $('.modal-error-msg').html(json_data.error.message);
                    } else {
                        show_thumbs_gallery(linkId);
                        $('.photo-gallery').children().removeClass('blur');
                        manageBilling(json_data.clisender, json_data.clireciever);
                    }
                },
                error: function() {
                    console.log('Ajax error');
                },
            });
            return false;
        })
    });
}

function make_profile_picture_link(currentIndex) {
    var pic_id = $('#baguette-img-' + currentIndex + '> figure > img').attr('alt');
    html = '<a class="make-profile" id="' + pic_id + '">Make my profile picture</a>'
    if ($('#baguette-img-' + currentIndex + '> figure > a').attr('id') == null) {
        $('#baguette-img-' + currentIndex + '> figure').append(html);
        var screen_heigth = $('.full-image').height();
        var img_heigth = $('#baguette-img-' + currentIndex + '> figure > img').height();
        var position = (screen_heigth / 2) + (img_heigth / 2) + 'px';
        $('#baguette-img-' + currentIndex + '> figure > a').css({
            'top': position
        });
    }
}

function resize_album_preview() {
    if ($(window).width() > 992) {
        var w = $(window).width() - $('.profile').width() - $('#chatContainer').width() - 50;
        $('#members-content').width(w);
        if ($('#members-content').width() < 140) {
            $('#members-content').hide();
            $('#btn-go-top').hide();
        } else {
            var clase;
            var remove = "col-lg-12 col-lg-4 col-lg-6";
            if ($('#members-content').width() < 250) {
                clase = "col-lg-12";
            } else if ($('#members-content').width() > 900) {
                clase = "col-lg-4";
            }
            else{
                clase = "col-lg-6";
            }
            $("div[name=list_members]").each(function() {
                $(this).removeClass(remove);
                $(this).addClass(clase);
            });
            $('#members-content').show();
            $('#btn-go-top').show();
        }
    }
    width_container = $('.profile_picture').width();
    width_pic = $('#picture-preview').width();
    margin_left = Math.round((width_pic / 2) - (width_container / 2), 2);
    $('#picture-preview').css({
        'margin-left': '-' + margin_left + 'px'
    });

    item_width = $('.album-preview').width();

    $('.album-preview').each(function() {
        $('.album-preview').height(item_width);
        $(this).find('img').css('width', '100%');
        $(this).find('img').css('min-height', '100%');
    });
    collage();
}

function get_thumb_size(album_length) {
    if (album_length >= 3 && album_length <= 9) {
        return 2;
    }
    if (album_length >= 10 && album_length <= 15) {
        return 3;
    }
    return 2;
}

function show_suggestions(url) {
    $.ajax({
        type: 'POST',
        url: url,
        dataType: 'json',
        data: {},
        success: function(json_members) {
            showClientList(json_members, false);
            $('#members-content').append(showClientList(json_members));
            var clase = "col-lg-6";
            if ($('#members-content').width() < 250) {
                clase = "col-lg-12";
            }
            $("div[name=list_members]").each(function() {
                $(this).removeClass("undefined");
                $(this).addClass(clase);
            });
            resize_preview();
        },
        error: function() {
            console.log('Ajax error scrolling');
        },
    });
}

function delete_album(album_id) {
    $('#deletealbumModal').modal('show');
    $('#deletealbumModal').on('shown.bs.modal', function(e) {
        e.preventDefault();
        $('#btndeleteYes').unbind('click').click(function() {
            $.ajax({
                type: 'POST',
                url: deletealbum_url,
                data: {
                    'album_id': album_id
                },
                success: function(data) {
                    $('#deletealbumModal').modal('hide');
                    get_albums();
                    album = JSON.parse(o_album_list)
                    show_thumbs_gallery(album[album.length - 1].album.name);
                }
            });
        });
        return false;
    });
};

function get_albums() {
    $.ajax({
        type: 'POST',
        url: getalbums_url,
        success: function(results) {
            albums_member(results);
            resize_album_preview();
        }
    });
}

function show_message(message) {
    // Remove the error element
    pictures_to_upload.pop();
    $('#display-msg').html('<label>' + message + '</label>');
    $('#messageModal').modal('show');
}
