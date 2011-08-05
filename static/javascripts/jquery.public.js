uid = window.location.pathname.substr(2,window.location.pathname.indexOf('/',1)-2); //Impure convenience

var _getInfo = function(url) {
    $.ajax({
       type: "GET",
       url: url,
       dataType: 'json',
       success: _swapContent,
       error: _failedContent
    });
    return;
};

var _failedContent = function(){alert('Failed to get content!');};

var _createFolders = function(data) {
    if (data.folders && data.folders.length > 0) {
        var asideContents = "<ol class='folders'>";
        $.each(data.folders, function(index, value){ 
            name = value.substring(value.lastIndexOf('/')+1);
            link = "\n<li><a href='/u"+uid + value + "'>"+name+'</a></li>';
            asideContents = asideContents + link;
        });
        asideContents = asideContents + "\n</ul>";
        aside.html(asideContents);
    }
};

var _createMedia = function(data) {
    var asideContents = aside.html();
    if (data.files && data.files.length > 0) {
        asideContents = asideContents + '\n<ul class="files">';
        $.each(data.files, function(index,value){
            var url = 'http://dl.dropbox.com/u/' + uid + value;
            var name = value.substring(value.lastIndexOf('/')+1);
            //alert(url);
            var link = '<li><a href="'+ url + '">'+name+'</a></li>\n';
            asideContents = asideContents + link;
        });
        asideContents = asideContents + '\n</ul>';
    }
    if (data.images && data.images.length > 0) {
        asideContents = asideContents + '\n<ul class="images">';
        $.each(data.images, function(index, value){
            var url = 'http://dl.dropbox.com/u/' + uid + value;
            //alert(url);
            var img = '<li><a href="'+ url + '"><img src="'+url+'"></img></a></li>\n';
            asideContents = asideContents + img;
        });
        asideContents = asideContents + "\n</ul>";
    }
    aside.html(asideContents);
};

var buildPage = function(publicData) {
    _getInfo(window.location.pathname +'/info.txt');
    _createFolders(publicData);
    _createMedia(publicData);
};

var wrongPass = function(publicData) {
    //HARLAN: Fix me
    alert("Wrong Password");
};

jQuery(document).ready(function($) {
    if(document.cookie != '' && document.cookie.search('pw\-') != -1) {
        $.ajax({
            type: "POST",
            url: window.location.pathname,
            data: "pw=cookie",
            success: buildPage        
        });
    }
    $('#passwordGo').click(function(){
        var pass = $('#passwordBox').val();
        $.ajax({
          type: "POST",
          url: window.location.pathname,
          data: "pw=" + escape(pass),
          success: buildPage,
          error: wrongPass
        });
        return false;
    });
});