$(document).ready(function() {
    show_more(url);
    var cad = "";
    $("div[name=list_members]").each(function() {
        var id = $(this).attr("id").split("_")[1];
        cad = (cad == "" ? id : cad + "," + id);
        $("#client_list_id").val(cad);
    });
});
