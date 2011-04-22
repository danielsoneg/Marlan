function pageLandingInteractions(context){
    getInfo();
}

jQuery(document).ready(function($) {
  var context = '#page_landing';
  $(context).runOnScope(function(){
    var pageLanding = new pageLandingInteractions(context);
  });
  $('.text_content, .header_content').blur(function() {
      var content = $('.header_content').html() + "~~~~" + $('.text_content').html();
      //alert("Sending: " +newValue);
      $.ajax({
         type: "POST",
         url: window.location.pathname,
         data: "text=" + escape(content) + "&action=write",
         success: editCallback
      });
  });
});

function getInfo() {
    url = window.location.pathname +'/info.txt';
    $.ajax({
       type: "GET",
       url: url,
       success: swapContent
    });
    return;
}

function swapContent(content) {
    head = "";
    body = content;
    if (content.indexOf('~~~~') >= 0) {
        content = content.split('~~~~',2);
        head = content[0];
        body = content[1];
    };
    $('.header_content').html(head);
    $('.text_content').html(body);
    $('a').click(function(){ window.location=$(this).attr('href'); });
}

function editCallback(data) {
    data = jQuery.parseJSON(data);
    if (data.Code == 1) {
        swapContent(data.Message);
    }
}