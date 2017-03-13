$(document).ready(function() {
    $("#profileContainer").on("click", ".older", showInboxMessage);
    $("#profileContainer").on("click", "#input_inbox", cleanInbox);
    $("#profileContainer").on("blur", "#input_inbox", putInbox);
    $("#profileContainer").on("click", "#send_mail", function() {
        var sender = $("#sender").val();
        var reciever = $("#recieved_mail").val();
        var origin = $("#inbcodeorigin").val();
        var msg = $.trim($("#input_inbox").text());
        var title = '';
        sendInbox(sender, reciever, origin, msg, title);
    });
    $("#profileContainer").on("click", "#send_new_mail", function() {
        var sender = $("#sender").val();
        var reciever = $("#ids").val();
        var origin = 0;
        var msg = $.trim($("#input_new_inbox").text());
        var title = $("#title").val();
        sendInbox(sender, reciever, origin, msg, title);
    });
    $("#profileContainer").on("click", "#new_mail", lookClientInbox);
    $("#profileContainer").on("click", "#btn-next", function() {
        if ($(this).text() == "NEXT") {
            drawForm();
        } else {
            $("#mis-contactos").html("");
            lookClientInbox();
            $("#btn-next").text("NEXT");
        }
    });
});

function lookClientInbox() {
    $.ajax({
        url: '/ajax/clients/',
        dataType: 'json',
        type: 'POST',
        data: {
            'girl': $("#sender").val(),
        },
        success: function(json_members) {
            drawClient(json_members, true);
            $('#myModal').modal({
                target: '.bd-example-modal-lg',
            });
        }
    });
}

function drawForm() {
    var clients = "";
    var ids = "";
    var i = 0;
    $(".checkbox:checked").each(function() {
        i++;
        var id = $(this).attr("id").split("_")[1];
        if (i == $(".checkbox:checked").length) {
            clients += $("#profile_" + id + ">.profile-info>strong>a>b").text();
            ids += id;
        } else {
            clients += $("#profile_" + id + ">.profile-info>strong>a>b").text() + ", ";
            ids += id + ",";
        }
        $("#profile_" + id + ".profile-info>strong>a>b").text();
    });
    if (i == 0) {
        alert("Select at least one recipient");
    } else {
        html = addForm2(clients, ids);
        $("#mis-contactos").html("");
        $("#mis-contactos").append(html);
        $("#btn-next").text("BACK");
    }
}

function drawClient(json_members) {
    if (json_members['error'] != null) {
        if (json_members['error'] == 'yes') {
            $("#mis-contactos").append(json_members['description']);
        } else {
            $("#mis-contactos").append(json_members['error']);
        }
    } else {
        client_list = JSON.parse(json_members);
        for (var member in client_list) {
            var id = client_list[member].pk;
            var current = client_list[member].fields;
            html = '<div id="profile_' + id + '" class="profile-preview">';
            html += '<div class="select">';
            html += '<input type="checkbox" class="checkbox" id="check_' + id + '" name="check" />';
            html += '<label for="check_' + id + '"><span></span></label>';
            html += '</div>';
            html += '<div class="profile-member">'
            html += '<img class="pic-profile" src="' + current.profile_picture + '" alt="' + current.cliusername + '" />';
            if (current.feecode != null) {
                html += '<div class="feel">';
                html += '<img src="' + current.feecode + '" />';
                html += '</div>';
            }
            html += '</div>';
            html += '<div class="profile-info">';
            html += '<strong>';
            html += '<a href="/profile/' + current.cliusername + '">';
            html += '<b>@' + current.cliusername + '</b>';
            html += '</a>';
            if (current.clibirthdate != null) {
                html += ', ' + current.age;
            }
            html += '</strong>'
            if (current.cliname != null) {
                html += '<br />' + current.cliname;
            }
            if (current.citcode != null) {
                html += '<br />' + current.citcode;
            }
            html += '</div>';
            html += '</div>';
            $("#mis-contactos").append(html);
        }
    }
}

function cleanInbox() {
    var text = $.trim($(this).text());
    if (text == "Click here to Reply") {
        $(this).text("");
    }
}

function putInbox() {
    var text = $.trim($(this).text());
    if (text == "") {
        $(this).text("Click here to Reply");
    }
}

function sendInbox(sender, reciever, origin, msg, title) {
    if (msg != "") {
        $.ajax({
            url: '/ajax/send/inbox/',
            dataType: 'json',
            type: 'POST',
            data: {
                'girl': sender,
                'recieved': reciever,
                'origin': origin,
                'msg': msg,
                'title': title
            },
            success: function(data) {
                if (data["error"] == "no") {
                    var li = "";
                    for (j = 0; j < data["inbox"].length; j++) {
                        var i = data["inbox"][j];
                        if (i["inbcodeorigin"] == null) { //Es un mensaje nuevo
                            $('#myModal').modal('hide');
                            $(".current_inbox").removeClass("current_inbox");
                            li = addClienInbox(' class="current_inbox"', i["inbcode"], i["inbpicturerecieved"], i["inbuserrecieved"], i["inbagerecieved"], i["inbnamerecieved"], i["inbshorttitle"], i["inbshortsenddate"], "Sent", true, i["inbclicoderecieved"]);
                            $(".clientsmyinbox").prepend(li);
                            if (j == (data["inbox"].length - 1)) { //Es el ultimo, se va a mostrar el mensaje
                                $(".history-mail").remove();
                                second_col = $('<div class="history-mail col-xs-9"></div>');
                                var myhistorymails = $('<div class="history"></div>');
                                li = addMessageInbox("current", i["inbcode"], i["inbtitle"], i["inbsenddate"], i["inbmessage"], i["inbclicodesent"], i["inbclicoderecieved"]);
                                myhistorymails.append(li);
                                second_col.append(myhistorymails);
                                var origin = i["inbcode"];
                                li = addForm(origin);
                                second_col.append(li);
                                $("#div_inbox").append(second_col);
                                setTimeout(function() {
                                    hasScrollBar(".history");
                                }, 500);
                            }
                        } else { //Es una respuesta
                            $(".history>.current").removeClass("current").addClass("older");
                            clase = "current";
                            li = addMessageInbox(clase, i["inbcode"], i["inbtitle"], i["inbsenddate"], i["inbmessage"], i["inbclicodesent"], i["inbclicoderecieved"]);
                            $(".history").append(li);
                            setTimeout(function() {
                                hasScrollBar(".history");
                            }, 500);
                            $("#input_inbox").html('Click here to <a class="reply" href="#">Reply</a>');
                            var objLi = $(".clientsmyinbox>li.current_inbox");
                            objLi.find(".itemtitle").text(i["inbshorttitle"]);
                            objLi.find(".tipdate").text(i["inbshortsenddate"]);
                            objLi.find(".tipstatus").text("Sent");
                            if (objLi.find(".sobre").attr("alt") != "Message read") {
                                objLi.find(".sobre").attr("alt", "Message read");
                                objLi.find(".sobre").attr("src", "/static/dateSite/img/blanco_02.png");
                            }
                        }
                    }
                } else {
                    alert(data["description"]);
                }
            }
        });
    } else {
        alert("El correo debe contener un mensaje");
    }
}

function showInboxMessage() {
    if ($(this).find(".inb-message").is(":visible")) {
        $(this).find(".inb-message").hide();
    } else {
        $(this).find(".inb-message").show();
    }
}

function updateQtyInbox(changer, literal) {
    //changer is the number to increase/decrease the current inbox quantity
    //literal is if the changer is a modifier or is a literal number
    if (literal == true) {
        var qT = changer;
    } else {
        var qT = parseInt($(".qty_inbox").text());
        qT = eval(qT + changer);
    }
    if (qT <= 0) {
        $(".qty_inbox").text(0);
        $(".inboxquantity").text(0).hide();
    } else if (qT > 9) {
        $(".qty_inbox").text(qT);
        $(".inboxquantity").text("+9").show();
    } else {
        $(".qty_inbox").text(qT);
        $(".inboxquantity").text(qT).show();
    }
}

function getQtyInbox(girl) {
    $.ajax({
        url: '/ajax/qty/inbox/',
        dataType: 'json',
        type: 'POST',
        data: {
            'clicode': girl
        },
        success: function(data) {
            var now_qty = parseInt(data["qty"]);
            updateQtyInbox(now_qty, true);
        }
    });
}

function getGirlInbox() {
    $.ajax({
        url: '/ajax/list/inbox/',
        dataType: 'json',
        type: 'POST',
        data: {
            'girl': $("#sender").val()
        },
        success: function(data) {
            if (data["error"] == 'yes') {
                var objPro = $("#profileContainer");
                var inbox = $('<div id="div_inbox" class="inbox row">' + data["description"] + '</div>');
                objPro.append(inbox);
            } else {
                var objPro = $("#profileContainer");
                if (data["inbox"].length > 0) {
                    var inbox = $('<div id="div_inbox" class="inbox row"></div>');
                    first_col = $('<div class="clients-mail col-xs-3"></div>');
                    button = $('<button type="button" class="new_mail" name="new_mail" id="new_mail">COMPOSE</button>');
                    first_col.append(button);
                    var modal = '<div class="modal fade bd-example-modal-lg" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myLargeModalLabel" aria-hidden="true">';
                    modal += '<div class="modal-dialog modal-lg" role="document">';
                    modal += '<div class="modal-content">';
                    modal += '<div class="modal-header">';
                    modal += '<h5 class="modal-title" id="exampleModalLabel">New Message</h5>';
                    modal += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
                    modal += '<span aria-hidden="true">&times;</span>';
                    modal += '</button>';
                    modal += '</div>';
                    modal += '<div class="modal-body">';
                    modal += '<h4>Select the mail recipients</h4>';
                    modal += '<div class="miscontactos" id="mis-contactos">';
                    modal += '</div>';
                    modal += '</div>';
                    modal += '<div class="modal-footer">';
                    modal += '<button type="button" class="btn btn-close btn-secondary" data-dismiss="modal">Close</button>';
                    modal += '<button type="button" id="btn-next" class="btn btn-next btn-primary">NEXT</button>';
                    modal += '</div>';
                    modal += '</div>';
                    modal += '</div>';
                    modal += '</div>';
                    first_col.append(modal);
                    //Este es el for de los clients
                    var clientsmyinbox = $('<ul class="clientsmyinbox"></ul>');
                    var li = "";
                    for (i = 0; i < data["inbox"].length; i++) {
                        act = data["inbox"][i];
                        if (i == 0) {
                            clase = ' class="current_inbox"';
                            $("#recieved_mail").val(act.clicode);
                        } else {
                            clase = '';
                        }
                        li = addClienInbox(clase, act.msg_id, act.clipicture, act.cliusername, act.cliage, act.cliname, act.msg_title, act.msg_date, act.msg_status, act.msg_read, act.clicode);
                        clientsmyinbox.append(li);
                    }

                    first_col.append(clientsmyinbox);

                    second_col = $('<div class="history-mail col-xs-9"></div>');
                    li = "";
                    var cat_last_mail = data["last_mail"].length;
                    if (cat_last_mail > 3) {
                        li = '<div class="qty_old_msg" id="qty_old_msg">MORE PREVIEW MESSAGES</div>';
                    }
                    //Este es el for de los correos
                    var myhistorymails = $('<div class="history"></div>');
                    if (cat_last_mail > 0) {
                        for (i = 0; i < cat_last_mail; i++) {
                            act = data["last_mail"][i];
                            clase = ((i == (cat_last_mail - 1)) ? "current" : "older");
                            li = li + addMessageInbox(clase, act.inbcode, act.inbtitle, act.inbsenddate, act.inbmessage, act.inbclicodesent, act.inbclicoderecieved);
                            myhistorymails.append(li);
                            li = "";
                        }
                    }
                    second_col.append(myhistorymails);

                    var origin = act.inbcodeorigin;
                    if (!$.isNumeric(act.inbcodeorigin)) {
                        origin = act.inbcode;
                    }
                    li = addForm(origin);

                    second_col.append(li);

                    inbox.append(first_col);
                    inbox.append(second_col);

                    var qty = data["qty_inbox"];
                    updateQtyInbox(qty, true);
                } else {
                    $(".inboxquantity,.qty_inbox").text("0").hide();
                    var inbox = $('<div id="div_inbox" class="inbox row">Without mails</div>');
                }
                objPro.append(inbox);
            }
        }
    });
    $("#profileContainer").on("click", ".read", showInboxMessage);
}

function getHistoryInbox() {
    var objImg = $(".clientsmyinbox>li.current_inbox .sobre");
    var status = objImg.attr("alt");
    var sobre = "/static/dateSite/img/";
    if (status == "Message read") {
        sobre += "gris_02.png";
    } else {
        sobre += "gris_01.png";
    }
    objImg.attr("src", sobre);
    $(".clientsmyinbox>li.current_inbox").removeClass("current_inbox");

    $(this).addClass("current_inbox");
    var objImg = $(this).find(".sobre");
    status = objImg.attr("alt");
    objImg.attr("src", "/static/dateSite/img/blanco_02.png");
    objImg.attr("alt", "Message read");
    var id = $(this).attr("id").split("_")[1];
    var cli_code = $(this).attr("id").split("_")[2];
    $("#recieved_mail").val(cli_code);
    $.ajax({
        url: '/ajax/get/inbox/',
        dataType: 'json',
        type: 'POST',
        data: {
            'inbcode': id,
            'clicode': $("#sender").val()
        },
        success: function(data) {
            var cat_last_mail = data["last_mail"].length;
            if (cat_last_mail > 0) {
                $(".history-mail").remove();
                second_col = $('<div class="history-mail col-xs-9"></div>');
                li = "";
                if (cat_last_mail > 3) {
                    li = li + '<div class="qty_old_msg" id="qty_old_msg">MORE PREVIEW MESSAGES</div>';
                }
                //Este es el for de los correos
                var myhistorymails = $('<div class="history"></div>');
                if (cat_last_mail > 0) {
                    for (i = 0; i < cat_last_mail; i++) {
                        act = data["last_mail"][i];
                        clase = ((i == (cat_last_mail - 1)) ? "current" : "older");
                        li = li + addMessageInbox(clase, act.inbcode, act.inbtitle, act.inbsenddate, act.inbmessage, act.inbclicodesent, act.inbclicoderecieved);
                        myhistorymails.append(li);
                        li = "";
                    }
                }
                second_col.append(myhistorymails);
                var origin = act.inbcodeorigin;
                if (!$.isNumeric(act.inbcodeorigin)) {
                    origin = act.inbcode;
                }
                li = addForm(origin);
                second_col.append(li);

                $("#div_inbox").append(second_col);
                if (status == "Message not read") {
                    updateQtyInbox(-1, false);
                }
                setTimeout(function() {
                    hasScrollBar(".history");
                }, 500);
            }
        }
    });
}

function addClienInbox(clase, id, pic, user, age, name, title, date, status, read, clicode) {
    var li = "";
    li = li + '<li id="inbox_' + id + '_' + clicode + '"' + clase + '>';
    li = li + '<div class="block-identity">';
    li = li + '<img class="itemimage" src="' + pic + '" alt="@' + user + '">';
    li = li + '</div>';
    li = li + '<div class="info-message">';
    if (age == 0) {
        li = li + '<span class="itemname">@' + user + '</span>';
    } else {
        li = li + '<span class="itemname">@' + user + ', ' + age + '</span>';
    }
    if (name != "") {
        li = li + '<span class="itemmessage">' + name + '</span>';
    }
    li = li + '<span class="itemtitle">' + title + '</span>';
    li = li + '</div>';
    li = li + '<div class="tips-message">';
    li = li + '<span class="tipdate">' + date + '</span>';

    li = li + '<span class="tipstatus">' + status + '</span>';

    if (clase == "") {
        sobre = "/static/dateSite/img/";
        if (status == "Sent") {
            sobre += "gris_02.png";
            alt = "Message read";
        } else {
            sobre += (read) ? "gris_02.png" : "gris_01.png";
            alt = (read) ? "Message read" : "Message not read";
        }
    } else {
        sobre = "/static/dateSite/img/";
        if (status == "Sent") {
            sobre += "blanco_02.png";
            alt = "Message read";
        } else {
            sobre += (read) ? "blanco_02.png" : "blanco_01.png";
            alt = (read) ? "Message read" : "Message not read";
        }
    }
    li = li + '<img class="sobre" src="' + sobre + '" alt="' + alt + '">';
    li = li + '</div>';
    li = li + '</li>';
    return li;
}

function addMessageInbox(clase, id, title, date, message, codesent, coderecieved) {
    li = '<div class="row ' + clase + '" id="msg_' + id + '">';
    li = li + '<div class="col-xs-9 inb-tittle">' + title + '</div>';
    li = li + '<div class="col-xs-3 inb-dateinbox">';
    li = li + '<span class="inb-date">' + date + '</span>';
    if ($("#sender").val() == coderecieved) {
        li = li + '<span class="inb-status">Recieved</span>';
    } else {
        li = li + '<span class="inb-status">Sent</span>';
    }
    li = li + '</div>';
    li = li + '<div class="col-xs-12 inb-message">' + message + '</div>';
    li = li + '</div>';
    return li;
}

function addForm(origin) {
    var li = '<form id="send_inbox"  class="row form_send_inbox">';
    li += '<div class="input_inbox" id="input_inbox" contenteditable="true">';
    li += 'Click here to <a class="reply" href="#">Reply</a>';
    li += '</div>';
    li += '<div class="input_buttom">';
    li += '<input type="button" class="send_mail" value="SEND MAIL" name="send_mail" id="send_mail" />';
    li += '<input type="button" class="attach_file" value="Attach files" name="attach_file" id="attach_file" />';
    li += '<input type="hidden"  value="' + origin + '" name="inbcodeorigin" id="inbcodeorigin" />';
    li += '</div>';
    li += '</form>';
    return li;
}

function addForm2(clients, ids) {
    var li = '<form id="send_new_inbox"  class="row form_send_inbox">';
    li += '<label>To</label>';
    li += '<input type="text" name="to" id="to" value="' + clients + '" readonly />';
    li += '<input type="hidden" name="ids" id="ids" value="' + ids + '" />';
    li += '<label>Title</label>';
    li += '<input type="text" name="title" id="title" />';
    li += '<div class="input_inbox" id="input_new_inbox" contenteditable="true">';
    li += '</div>';
    li += '<div class="input_buttom">';
    li += '<input type="button" class="send_mail" value="SEND MAIL" name="send_new_mail" id="send_new_mail" />';
    li += '<input type="button" class="attach_file" value="Attach files" name="attach_file" id="attach_file" />';
    li += '</div>';
    li += '</form>';
    return li;
}
