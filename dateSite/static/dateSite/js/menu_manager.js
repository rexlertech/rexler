$(document).ready(function(){
    $(".alert-header").hide();
    var q = parseInt($(".alertsquantity").text());
    if(q<=0) {$(".alertsquantity").hide();}
    q = parseInt($(".inboxquantity").text());
    if(q<=0) {$(".inboxquantity").hide();}
    $(".new_messages").each(function(){
        var q = parseInt($(this).text());
        if(q<=0){$(this).hide();}
    });
    $(".ul_girl>li").click(function(){
        var obj = $(this).attr("id").split("_")[1];
        closeChat();
        if($("#div_inbox").is(":visible")){
            $("#div_inbox").remove();
            $(".header-girl,.detail-info-girl").show();
        }
        getGirlInfo(obj);
        getListChat(obj);
        getQtyNotif(obj);
        getQtyInbox(obj);
    });
    $('#menu-alerts').click(function() {
        getGirlNotifications();
    });
    
    $('#menu-inbox').click(function(){
        getGirlInbox();
        $(".header-girl,.detail-info-girl").hide();
        setTimeout(function(){hasScrollBar(".history");},500);
    });
    $('#menu-profile-girl').click(function(){
        var obj = $("#sender").val();
        closeChat();
        if($("#div_inbox").is(":visible")){
            $("#div_inbox").remove();
            $(".header-girl,.detail-info-girl").show();
        }
        getGirlInfo(obj);
    });
    $("#profileContainer").on("click",".clientsmyinbox>li",getHistoryInbox);
});
function getGirlNotifications(){
    $.ajax({
        url: '/ajax/notifications/',
        dataType: 'json',
        type: 'POST',
        data:{'girl': $("#sender").val()},
        success: function (data) {
            var objNot = $("#notifications");
            if(data.length>0){
                var row ="";
                objNot.html('');
                for(i=0;i<data.length;i++){
                    row = $('<div class="notification row"></div>');
                    img = '<div class="col-xs-3"><img src="'+data[i].notpicture+'"></div>';
                    row.append(img);
                    date = '<span class="date">'+data[i].notdate+'</span>';
                    tex = '<div class="col-xs-9 description">'+data[i].notdescription+date+'</div>';
                    row.append(tex);
                    objNot.append(row);
                }
                updateAlerts();
            }
            else{
                $(".alertsquantity").text("0").hide();
                objNot.html('<div class="notification description row">Without new notifications</div>');
            }
        }
    });
}
function updateAlerts(){
    $.ajax({
        url: '/ajax/update/noti/',
        dataType: 'json',
        type: 'POST',
        data:{'quantity': 5,'girl':$("#sender").val()},
        success: function (data) {
            if(data['error'] == 'yes'){
                alert(data["description"]);
            }
            else{
                var now_qty = parseInt(data["qty"]);
                var old_qty = parseInt($(".qty_alerts").text());
                update_qty = eval(old_qty - now_qty);
                update_qty = -Math.abs(update_qty);
                updateQtyTotal($("#sender").val(),update_qty,false);
                updateQtyNotification(now_qty,true);
                updateQtyInbox(now_qty,true);
            }
        }
    });
}
function updateQtyNotification(changer,literal){
    //changer is the number to increase/decrease the current notification quantity
    //literal is if the changer is a modifier or is a literal number
    if(literal == true){
        var qT = changer;
    }
    else{
        var qT = parseInt($(".qty_alerts").text());
        qT = eval(qT + changer);
    }
    if (qT <= 0){
        $(".qty_alerts").text(0);
        $(".alertsquantity").text(0).hide();
    }
    else if(qT > 9){
        $(".qty_alerts").text(qT);
        $(".alertsquantity").text("+9").show();
    }
    else{
        $(".qty_alerts").text(qT);
        $(".alertsquantity").text(qT).show();
    }
}
function updateQtyTotal(clicode,changer,literal){
    //changer is the number to increase/decrease the current total quantity
    if (literal==true){
        var qT = parseInt(changer);
    }else{
        var qT = parseInt($("#girl_"+clicode+">.qty_messages").text());
        qT = eval(qT + changer);
    }
    if (qT <= 0){
        $("#girl_"+clicode+">.qty_messages").text(0);
        $("#girl_"+clicode+">.new_messages").text(0).hide();
    }
    else if(qT > 9){
        $("#girl_"+clicode+">.qty_messages").text(qT);
        $("#girl_"+clicode+">.new_messages").text("+9").show();
    }
    else{
        $("#girl_"+clicode+">.qty_messages").text(qT);
        $("#girl_"+clicode+">.new_messages").text(qT).show();
    }
}
function getGirlInfo(girl){
    event.preventDefault();
    $.ajax({
        url: '/ajax/infogirl/',
        dataType: 'json',
        type: 'POST',
        data:{
            'girl': girl
        },
        success: function (data) {
            $('#sender').val(data.clicode);
            //Select mnu girl
            $(".ul_girl>li.girl_selected").removeAttr("class");
            $(".ul_girl>li#girl_"+data.clicode).attr("class","girl_selected" );
            $("#mnu_profile").attr("src",data.clipicture);
            //Header
            var username = "@"+data.cliusername;
            if (parseInt(data.cliage)>0){
                username = username+", "+data.cliage
            }
            var name=(data.cliname!="")?data.cliname:"";
            var city=(data.clicity!="")?data.clicity:"";
            var description = ""
            if(data.clidescription!="" && data.clidescription != null)
                description = '<span class="sum_title">About me&nbsp;</span>'+
                               data.clidescription;

            var header = $(".header-girl");
            header.find("img").attr("src",data.clipicture);
            var summary = header.find(".client_summary>p");
            summary.eq(0).text(username);
            summary.eq(1).text(name);
            summary.eq(2).text(city);
            summary.eq(3).html(description)

            var detail = $(".detail-info-girl");
            //Basic info
            var basic= detail.find(">.card").eq(0).find(">div").eq(1).find(">.card-block");

            var first_row = basic.find(">.row").eq(0);
            var gender=data.cligender
            first_row.find(">.card-description").eq(0).text(gender);
            var marital = data.climarital
            first_row.find(">.card-description").eq(1).text(marital);
            var ethnicity = data.cliethnicity
            first_row.find(">.card-description").eq(2).text(ethnicity);
            var second_row = basic.find(">.row").eq(1);
            var height = data.cliheight
            second_row.find(">.card-description").eq(0).text(height);
            var weight = data.cliweight
            second_row.find(">.card-description").eq(1).text(weight);
            var third_row = basic.find(">.row").eq(2);
            var education = data.clieducation
            third_row.find(">.card-description").eq(0).text(education);
            var ocuppation = data.cliocupation
            third_row.find(">.card-description").eq(1).text(ocuppation);
            var income = data.cliincome
            third_row.find(">.card-description").eq(2).text(income);

            //Hobbies
            var hobbies = detail.find(">.card").eq(1).find(">div").eq(1).find(">.card-block>.row");
            if (data.clihobbies.length>0){
                hobbies.html('');
                for(i=0;i<data.clihobbies.length;i++){
                    hobbies.append('<div class="col-xs-2 card-description">'+data.clihobbies[i]+'</div>');
                }
            }
            else{
                hobbies.html('<div class="col-xs-12 card-title">Without hobbies to show</div>');
            }

            //Sports
            var sports = detail.find(">.card").eq(2).find(">div").eq(1).find(">.card-block>.row");
            if (data.clisports.length>0){
                sports.html('');
                for(i=0;i<data.clisports.length;i++){
                    sports.append('<div class="col-xs-2 card-description">'+data.clisports[i]+'</div>');
                }
            }
            else{
                sports.html('<div class="col-xs-12 card-title">Without sports to show</div>');
            }

            //Pets
            var pets = detail.find(">.card").eq(3).find(">div").eq(1).find(">.card-block");
            if (data.clipets.length>0){
                first_row = '<div class="row">'+
                                '<div class="col-xs-3 card-title">Pet</div>'+
                                '<div class="col-xs-3 card-title">Do you have?</div>'+
                                '<div class="col-xs-3 card-title">Do you like?</div>'+
                                '<div class="col-xs-3 card-title">Do you dislike?</div>'+
                            '</div>'
                pets.html(first_row);
                var row = "";
                for(i=0;i<data.clipets.length;i++){
                    row=$('<div class="row"></div>');
                    row.append('<div class="col-xs-3 card-title">'+data.clipets[i].petname+'</div>');
                    row.append('<div class="col-xs-3 card-description">'+data.clipets[i].pechave+'</div>');
                    row.append('<div class="col-xs-3 card-description">'+data.clipets[i].peclike+'</div>');
                    row.append('<div class="col-xs-3 card-description">'+data.clipets[i].pecdontlike+'</div>');
                    pets.append(row);
                }
            }
            else{
                pets.html('<div class="row"><div class="col-xs-12 card-title">Without pets information to show</div></div>');
            }

            //Feeling
            $("#feel-icon").attr("src",data.clifeelingpicture);
        }
    });
}
function getListChat(girl){
    $.ajax({
        url: '/ajax/list_chat/',
        dataType: 'json',
        type: 'POST',
        data:{
            'girl': girl
        },
        success: function (data) {
            var i = 0;
            $(".clientsrequest>li,.clientsmychat>li").each(function(){$(this).remove();});
            if(data["myrequest"].length > 0){
                i=0;
                while(data["myrequest"][0][i]!=undefined){
                    c = data["myrequest"][0][i];
                    if ($("#sender").val()==c.sentcode){
                        putOnClientList(".clientsrequest",c.recievedcode,c.recievedprofilepicture,c.recievedusername,c.recievedage,c.mescontent,c.msg_qty);
                    }
                    else{
                        putOnClientList(".clientsrequest",c.sentcode,c.sentprofilepicture,c.sentusername,c.sentage,c.mescontent,c.msg_qty);
                    }
                    i = i + 1;
                }
            }
            else{
                $(".clientsrequest").append('<li class="notchatlist">&nbsp;</li>');
            }
            if(data["mychats"].length > 0){
                i=0;
                while(data["mychats"][0][i]!=undefined){
                    c = data["mychats"][0][i];
                    if ($("#sender").val()==c.sentcode){
                        putOnClientList(".clientsmychat",c.recievedcode,c.recievedprofilepicture,c.recievedusername,c.recievedage,c.mescontent,c.msg_qty);
                    }
                    else{
                        putOnClientList(".clientsmychat",c.sentcode,c.sentprofilepicture,c.sentusername,c.sentage,c.mescontent,c.msg_qty);
                    }
                    i = i + 1;
                }
            }
            else{
                $(".clientsmychat").append('<li class="notchatlist">&nbsp;</li>');
            }
        }
    });
}
function putOnClientList(lista,code,picture,username,age,message,qty){
    if($(lista+">li.notchatlist").length>0){$(lista+">li.notchatlist").remove();}
    $(lista).prepend($("<li id='client_"+code+"'></li>"));
    var chat = $(lista+">li#client_"+code);
    var col1 = $('<div class="block-identity"></div>');
    var col2 = $('<div class="block-message"></div>');
    col1.append($('<img class="itemimage" src="'+picture+'" alt="'+username+'">'));
    if (qty>9) {
        qty ="+9";
        col1.append($('<div class="itemquantity">+9</div>'));
    } else if(qty<=0)
    {
        qty = 0;
        col1.append($('<div class="itemquantity">0</div>'));
    }
    else{
        col1.append($('<div class="itemquantity">'+qty+'</div>'));
    }

    if(age==0){
        col2.append('<span class="itemname">'+username+'</span>');
    }
    else{
        col2.append('<span class="itemname">'+username+', '+age+'</span>');
    }
    col2.append('<p class="itemmessage">'+message+'</p>');

    chat.append(col1).append(col2);
    var q = parseInt($(lista+">li#client_"+code+">.block-identity>.itemquantity").text());
    if (parseInt(q)==0) $(lista+">li#client_"+code+">.block-identity>.itemquantity").hide();
    else $(lista+">li#client_"+code+">.block-identity>.itemquantity").show();
}
function getQtyNotif(girl){
    $.ajax({
        url: '/ajax/qty/noti/',
        dataType: 'json',
        type: 'POST',
        data:{'clicode':girl},
        success: function (data) {
            var now_qty = parseInt(data["qty"]);
            updateQtyNotification(now_qty,true);
        }
    });
}
