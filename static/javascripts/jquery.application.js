function pageLandingInteractions(context){
    getInfo();
}

jQuery(document).ready(function($) {
  var context = '#page_landing';
  $(context).runOnScope(function(){
    var pageLanding = new pageLandingInteractions(context);
  });
  $('.text_content').blur(function() {
      var newValue = $(this).html();
      //alert("Sending: " +newValue);
      $.ajax({
         type: "POST",
         url: window.location.pathname,
         data: "text=" + escape(newValue) + "&action=write",
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
    $('.text_content').html(content);
    $('a').click(function(){ window.location=$(this).attr('href'); });
}

function editCallback(data) {
    data = jQuery.parseJSON(data);
    if (data.Code == 1) {
        swapContent(data.Message);
    }
}