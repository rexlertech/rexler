$(document).ready(function(){
    $(".chatForm").hide();
    $(".itemquantity").each(function(){
        var q = parseInt($(this).text());
        if (q<=0){
            $(this).hide();
        }
    });
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat/");

    //Events to open the chat
    eventsOpenChat();

    //Cuando le indique cerrar a la ventana de chat, que se cierre
    $("#closechat").on("click",function(e){e.preventDefault();closeChat();});
    //Cuando deja una conversacion
    $("#leave").on("click",function(e){e.preventDefault();leaveConversation();})

    //Cuando se envia un mensaje
    $("#message").keydown(function(event){
        var tecCode = event.which || event.keyCode;
        if(tecCode==13){ //Si presiona enter
            var mensaje = $.trim($("#message").html().replace(/<br>/g,""));
            sendMessage(mensaje,"mensaje");
            return false;
        }
        else if(tecCode==8 || tecCode==46){ //Si presiona backspace
            if($.trim($("#message").html())==""){
                cantidad=160;
            }
            else{
                var cantidad = parseInt($("#caracteres").text());
                cantidad++;
                cantidad = ((cantidad > 160) ? 160 : cantidad);
            }
            $("#caracteres").text(cantidad);
            return true;
        }
        else{
            //Debo filtrar el caracter; si si se puede escribir verifico
            //la disponibilidad en longitud
            return cantCaracteres();
        }
    });

    closeBoxEmojins();

    //Para enviar emojins o stickers
    $(".img_emoticon, .img_sticker").click(function(){
        var cantidad = parseInt($("#caracteres").text());
        if(cantidad>0){
            var imagen =  $(this).parent().html();
            if($(this).attr("class")==="img_sticker"){
                sendMessage(imagen,"sticker");
            }
            else{
                var mensaje = $("#message").html().replace(/<br>/g,"");
                $('#message').focus();
                $('#message').html(mensaje+imagen);
                cantidad=cantidad-1;
                $("#caracteres").text(cantidad);
            }
        }
    });
    $(".action-emojin, .action-sticker").click(manageEmojins);

    //Cuando se recibe un mensaje del servidor
    chatsock.onmessage = function(message) {
        $('#chatform').popover('dispose');
        var data = JSON.parse(message.data);
        var objerror = data.error;
        if(objerror.type=="1"){ // Error cuando no hay creditos
            $('#chatform').popover({
                content: objerror.message,
                title: 'CREDITS',
                trigger: 'manual',
                placement: 'top'
            });
            $('#chatform').popover('show');
            $("#message").attr("contentEditable",false);
            $("#send-message").removeClass("input-button").addClass("input-button-disable").off("click");
        }
        else if(objerror.type=="2"){ // El que recibe se fue de la pagina
            var msg = data.mensaje;
            var objsender = data.clientesen;
            var objreciever = data.clienterec;
            $('#chatform').popover({
                content: objerror.message,
                title: objerror.title,
                trigger: 'manual',
                placement: 'top'
            });
            $('#chatform').popover('show');
            evaluateMessage(objsender,objreciever,msg.mescontent,msg.mescontentshort,msg.mescode);
        }
        else if(objerror.type=="3"){ // Mensaje con alert
            var msg = data.notification;
            if(msg.clientrecieved==$('#sender').val()){//Si el que recibe es la chica que esta abierta
                var alerts = $("#notifications");
                var ele = $('<div class="notification row"></div>');
                ele.append($('<div class="col-xs-3"></div>').html('<img src="'+msg.clientpicture+'">'));
                ele.append($('<div class="col-xs-9 description">').html('@'+msg.ntymessage+'<span class="date">'+msg.ntydate+'</span>'));
                alerts.prepend(ele);
                if($(".notification").length>5){
                    $(".notification:last").remove();
                }
                updateQtyNotification(1,false);
            }
            var ind = "girl_"+msg.clientrecieved;
            if (exists(ind)){
                updateQtyTotal(msg.clientrecieved,1,false);
            }
        }
        else if(objerror.type=="4"){ // Correo electronico
            alert("llego un correo");
        }
        else if(objerror.type=="0"){
            var msg = data.mensaje;
            var objsender = data.clientesen;
            var objreciever = data.clienterec;
            evaluateMessage(objsender,objreciever,msg.mescontent,msg.mescontentshort,msg.mescode);
            hasScrollBar("#chat-messages");
        }
    };
});
function closeBoxEmojins(){
    $(".emoticones").hide();
    $(".the_stickers,.the_emojins").hide();
    $(".chat-messages").css("height","100%");
}
function manageEmojins(){
    if($(".emoticones").is(":visible")){
        if($(this).attr("id")=="emojin" && $(".the_stickers").is(":visible")){
            $(".the_emojins").show();
            $(".the_stickers,.price").hide();
        }
        else if($(this).attr("id")=="sticker" && $(".the_emojins").is(":visible")){
            $(".the_emojins").hide();
            $(".the_stickers,.price").show();
        }
        else{
            $(".emoticones").hide();
            $(".chat-messages").css("height","100%");
        }
    }
    else{
        if($(this).attr("id")=="emojin"){
            $(".the_emojins").show();
            $(".the_stickers,.price").hide();
        }
        else{
            $(".the_emojins").hide();
            $(".the_stickers,.price").show();
        }
        $(".chat-messages").css("height", function( index ) {
            var height = $(".chat-content").height();
            return height - 90;
        })
        $(".emoticones").show();
    }
}
function evaluateMessage(sender,reciever,message,messageshort,mescode){
    if(sender.clicode==$('#sender').val()){//Si el sender es el cliente actual
        //Busco si esta en mychatsvar
        inMychats = inList(".clientsmychat>li",reciever.clicode,message,messageshort);
        //Si esta en my chats,en la misma funcion ya se actualizo bagdet y message
        //Si no esta
        if(inMychats==false){
            //Agregamos el elemento a my chat
            updateClientList(".clientsmychat",reciever,message,messageshort);
            //Lo buscamos en my request y si existe lo borramos
            $(".clientsrequest>li:not(.notchatlist)").each(function(){
                if($(this).attr("id").split("_")[1]==reciever.clicode){
                    $(this).remove();
                    return;
                }
            });
            //Si la lista se quedo sin elementos, le colocamos que no hay
            if($(".clientsrequest>li").length<=0){
                $(".clientsrequest").append('<li class="notchatlist">&nbsp;</li>');
            }
        }
    }
    else{ //Si le estan escribiendo al cliente actual
        if (reciever.clicode == $('#sender').val()){
            inMychats = inList(".clientsmychat>li",sender.clicode,message,messageshort);
            if(inMychats==false){
                var inMyrequest = inList(".clientsrequest>li",sender.clicode,message,messageshort);
                if(inMyrequest===false){
                    updateClientList(".clientsrequest",sender,message,messageshort);
                }
            }
        }
        updateQtyTotal(reciever.clicode,1,false);
    }
    var roomId = chatName(sender.clicode,reciever.clicode);
    if (exists(roomId)==true) { //Si el mensaje es del chat abierto
        addMessage(sender.clicode,roomId,message);
        var new_client = reciever.clicode;
        if(sender.clicode!=$("#sender").val()){
            new_client=sender.clicode;
        }
        $("li#client_"+new_client).find(".itemquantity").text("0").hide();
        updateQtyTotal($("#sender").val(),$(".qty_alerts").text(),true);
        if($("#sender").val() == reciever.clicode){
            checkReadMessage(mescode);
        }
    }
}
function checkReadMessage(code){
    $.ajax({
        url: '/ajax/checkReadMessage/',
        dataType: 'json',
        type: 'POST',
        data:{
            'code': code
        }
    });
}
function sendMessage(message,type){
    if (message == ""){
        $('#chatform').popover({
            content: 'Type your messages, please.',
            title: 'Warning',
            trigger: 'manual',
            placement: 'top'
        });
        $('#chatform').popover('show');
        setTimeout(function(){ $('#chatform').popover('dispose'); }, 3000);
    }
    else{
        $('#chatform').popover('dispose');
        var message = {
            clicodesent: $('#sender').val(),
            clicoderecieved: $('#reciever').val(),
            mescontent: message,
            type: type,
        }
        chatsock.send(JSON.stringify(message));
        $("#message").html('').focus();
        $("#caracteres").text(160);
        closeBoxEmojins();
    }
}
function openChat(){
    $("#message").attr("contentEditable",true);
    $("#send-message").removeClass("input-button-disable").addClass("input-button");
    $("#send-message").on("click", function(event) {
        sendMessage($.trim($('#message').html()),"mensaje");
    });
    if($("#chat-box").is(":visible")==false){
        $("#chatContainer").removeClass("col-xs-2").addClass("col-xs-5");
        $("#profileContainer").removeClass("col-xs-10").addClass("col-xs-7");
        $("#chat-list").removeClass("chatList").addClass("chatListChat");
        $("#chat-box").show();
    }
}
function closeChat(){
    $('#chatform').popover('dispose');
    cleanChatBox();
    $("#chatContainer").removeClass("col-xs-5").addClass("col-xs-2");
    $("#profileContainer").removeClass("col-xs-7").addClass("col-xs-10");
    $("#chat-list").removeClass("chatListChat").addClass("chatList");
    $("#chat-box").hide();
}
function leaveConversation(){
    $.ajax({
        url: '/ajax/leaveconversation/',
        dataType: 'json',
        type: 'POST',
        data:{
            'reciever': $("#reciever").val(),
            'sender': $("#sender").val()
        },
        success: function (data) {
            $('#chatform').popover('dispose');
            if(data["error"]!="ok"){
                $('#chatform').popover({
                    content: data["error"],
                    title: 'Error',
                    trigger: 'manual',
                    placement: 'top'
                });
                $('#chatform').popover('show');
            }else{
                $("#credits_billing").text(data["credits"]);
                closeChat();
            }
        }
    });
}
function cleanChatBox(){
    $(".chat-header>.chat-image,.chat-header>.chat-fell").attr("src","");
    $(".chat-name,.chat-nickname,.chat-city").text("");
    $(".chat-messages").children().remove();
    $("#message").val("");
}
function chatName(number1,number2){
    var name="";
    if(parseInt(number1)<parseInt(number2)){
        name="chat_"+number1+"_"+number2;
    }
    else{
        name="chat_"+number2+"_"+number1;
    }
    return name;
}
function getMessages(reciever){
    $.ajax({
        url: '/ajax/messages/',
        dataType: 'json',
        type: 'POST',
        data:{
            'reciever': reciever,
            'sender': $("#sender").val()
        },
        success: function (data) {
            $("#reciever").val(reciever);
            if(data["cliente"].clireplychannel==null){
                gender = (data["cliente"].gencode == 1 || data["cliente"].gencode == 3)?"he":"she";
                $('#chatform').popover({
                    content: 'When @'+data["cliente"].cliusername+' connects, '+gender+' can see your messages',
                    title: '@'+data["cliente"].cliusername+' is offline',
                    trigger: 'manual',
                    placement: 'top'
                });
                $('#chatform').popover('show');
            }else{
                $('#chatform').popover('dispose');
            }
            $(".chat-img-container>.chat-image").attr("src",data["cliente"].clipicture);
            if(data["cliente"].clifeelingpicture!="no"){
                $(".picturechat>.chat-fell").attr("src",data["cliente"].clifeelingpicture);
                $(".picturechat>.chat-fell").show();
            }
            else{
                $(".picturechat>.chat-fell").hide();
            }
            if(data["cliente"].cliage>0){
                $(".identitychat>.chat-name").text("@"+data["cliente"].cliusername+", "+data["cliente"].cliage);
            }else{
                $(".identitychat>.chat-name").text("@"+data["cliente"].cliusername);
            }
            if(data["cliente"].cliname!="None"){
                $(".identitychat>.chat-nickname").text(data["cliente"].cliname);
            }
            else{
                $(".identitychat>.chat-nickname").text("");
            }
            if(data["cliente"].clicity!="None"){
                $(".identitychat>.chat-city").text(data["cliente"].clicity);
            }
            else{
                $(".identitychat>.chat-city").text("");
            }
            var roomId = chatName($("#sender").val(),reciever);
            if (exists(roomId)==false) {
                $("#chat-messages").append($("<ul id='"+roomId+"' class='message-list'></ul>"));
            }
            i=0;
            if(typeof data["mensajes"]!=="undefined"){
                while(typeof data["mensajes"][i] !== "undefined"){
                   addMessage(data["mensajes"][i].clicodesent,roomId,data["mensajes"][i].mescontent);
                   i=i+1;
                }
            }
            hasScrollBar("#chat-messages");
        }
    });
}
function eventsOpenChat(){
    $("#membersContainer").on("click",".action-icons",function(){
        var id = $(this).attr("id").split("_")[1];
        openChat();
        cleanChatBox();
        getMessages(id);
        setTimeout(function(){hasScrollBar("#chat-messages");},500);
    });
    $(".clientsmychat").on("click","li:not(.notchatlist)",function(){
        var id = $(this).attr("id").split("_")[1];
        openChat();
        cleanChatBox();
        getMessages(id);
        cleanBadget($(this));
        setTimeout(function(){hasScrollBar("#chat-messages");},500);
    });
    $(".clientsrequest").on("click","li:not(.notchatlist)",function(){
        var id = $(this).attr("id").split("_")[1];
        openChat();
        cleanChatBox();
        getMessages(id);
        cleanBadget($(this));
        setTimeout(function(){hasScrollBar("#chat-messages");},500);
    });
}
function cleanBadget(obj){
    updateQtyTotal($("#sender").val(),$(".qty_alerts").text(),true);
    obj.find(".block-identity>.itemquantity").text("0").hide();
}
function addMessage(sender,roomId,message){
    var clase="message-receiver";
    if(sender==$('#sender').val()){
        clase="message-sender";
    }
    var chat = $("#"+roomId);
    var ele = $('<li class="'+clase+'"></li>');
    ele.append($("<span></span>").html(message));
    chat.append(ele);
}
function updateClientList(lista,client,message,messageshort){
    if($(lista+">li.notchatlist").length>0){$(lista+">li.notchatlist").remove();}
    $(lista).prepend($("<li id='client_"+client.clicode+"'></li>"));
    var chat = $(lista+">li#client_"+client.clicode);
    var col1 = $('<div class="block-identity"></div>');
    var col2 = $('<div class="block-message"></div>');
    col1.append($('<img class="itemimage" src="'+client.clipicture+'" alt="'+client.cliusername+'">'));
    col1.append($('<div class="itemquantity">1</div>'));
    if(client.cliage==0){
        col2.append('<span class="itemname">'+client.cliusername+'</span>');
    }
    else{
        col2.append('<span class="itemname">'+client.cliusername+', '+client.cliage+'</span>');
    }
    col2.append('<p class="itemmessage">'+messageshort+'</p>');

    chat.append(col1).append(col2);
    chat.find(".itemquantity").show();
}
cantCaracteres = function(){
    var canMax = 160;
    var mensaje = $("#message").html().replace(/<br>/g,"");
    mensaje = mensaje.replace(/&nbsp;/g,"e");
    var encontrado = true;
    var indiceInicial = 0;
    var indiceFinal = 0;
    var new_mensaje = "";
    while(encontrado){
        indiceFinal = mensaje.indexOf('<img',indiceInicial);
        if(indiceFinal>=0){
            new_mensaje += mensaje.substring(indiceInicial, indiceFinal)+"i";
            indiceFinal = mensaje.indexOf('>',indiceFinal);
            indiceFinal++;
            mensaje = mensaje.substring(indiceFinal);
        } else{
            encontrado=false;
            new_mensaje+=mensaje;
        }
    }
    encontrado=false;
    var long =new_mensaje.length+1;
    if(long<=canMax){
        var cantidad = canMax - long;
        $("#caracteres").text(cantidad);
        encontrado=true;
    }
    return encontrado;
}
exists = function (roomId) {
    return $("#"+roomId).length > 0;
};
function hasScrollBar(element) {
    var obj1 = $(element);
    if(obj1.prop('scrollHeight') > obj1.height()){
        var scroll = obj1.prop('scrollHeight') - obj1.outerHeight();
        obj1.animate({scrollTop:scroll}, '500', 'swing');
    }
    return;
}
inList = function (listas,sender,message,messageshort){
    var resp = false;
    $(listas+":not(.notchatlist)").each(function(){
        if($(this).attr("id").split("_")[1]==sender){
            //Coloquemos el badget
            cant=parseInt($(this).find(".itemquantity").text());
            cant++;
            if(cant>9){cant="+9";}
            $(this).find(".itemquantity").text(cant).show();
            $(this).find(".itemmessage").html(messageshort);
            var i = $(this).index();
            if(i>0){
                var objLista = $(this).html();
                $(listas+"#client_"+sender).remove();
                $(listas).parent().prepend($("<li id='client_"+sender+"'>"+objLista+"</li>"));
                $(listas+"#client_"+sender).find(".itemquantity").text(cant).show();
            }
            resp=true;
            return;
        }
    });
    return resp;
}
