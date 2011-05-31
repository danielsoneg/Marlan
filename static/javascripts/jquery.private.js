var shareSet = function() {
    //Do stuff related to successfull password setting here.
    //writeMetadata();
    return;
};

var writeMetadata = function() {
    $.ajax({
        type: 'POST',
        url: window.location.pathname,
        data: 'action=metadata'
    });
};
jQuery(document).ready(function($) {
    $('#pwgo').click(function(){
        var pass = $('#pw').val();
        $.ajax({
          type: "POST",
          url: window.location.pathname,
          data: "pw=" + escape(pass) + "&action=share",
          success: shareSet
        });
        return false;
    });
});