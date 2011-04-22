function pageLandingInteractions(context){
    getInfo();
}

jQuery(document).ready(function($) {
  var context = '#page_landing';
  $(context).runOnScope(function(){
    var pageLanding = new pageLandingInteractions(context);
  });
});

function getInfo() {
    url = window.location.pathname +'/info.txt';
    $.ajax({
       type: "GET",
       url: url,
       success: gotInfo
    });   
}

function gotInfo(data) {
    $('.text_content').text(data);
}
